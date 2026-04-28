"""Requirement-focused integration tests for borrow, return, and renewal flows."""

import datetime

import pytest
from django.test import Client
from django.urls import reverse

pytestmark = [pytest.mark.integration_client, pytest.mark.django_db]


def test_borrow_requires_login(available_book_instance):
    """REQ-WF-002: Unauthenticated borrow redirects to login."""
    response = Client().post(reverse("borrow-book", args=[available_book_instance.pk]))
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_borrow_get_redirects_without_state_change(available_book_instance, member_user):
    """Non-POST borrow request redirects and leaves state unchanged."""
    client = Client()
    client.force_login(member_user)
    response = client.get(reverse("borrow-book", args=[available_book_instance.pk]))
    assert response.status_code == 302
    available_book_instance.refresh_from_db()
    assert available_book_instance.status == "a"


@pytest.mark.parametrize(
    ("next_url", "expected_location"),
    [
        ("books", "books"),
        ("http://evil.example.com/", "my-borrowed"),
    ],
)
def test_borrow_next_redirect_safety(
    available_book_instance, member_user, next_url, expected_location
):
    """Safe local next URLs are honoured; external URLs are rejected."""
    client = Client()
    client.force_login(member_user)
    value = reverse(next_url) if next_url == "books" else next_url
    response = client.post(
        reverse("borrow-book", args=[available_book_instance.pk]),
        data={"next": value},
    )
    assert response.status_code == 302
    assert reverse(expected_location) in response["Location"]


def test_borrow_success_sets_loan_fields_and_message(available_book_instance, member_user):
    """REQ-WF-003/007: Borrow success updates state and shows success flash."""
    client = Client()
    client.force_login(member_user)
    response = client.post(
        reverse("borrow-book", args=[available_book_instance.pk]),
        follow=True,
    )
    assert response.status_code == 200
    messages = [str(msg).lower() for msg in response.context["messages"]]
    assert any("borrowed" in msg for msg in messages)

    available_book_instance.refresh_from_db()
    assert available_book_instance.status == "o"
    assert available_book_instance.borrower == member_user
    assert available_book_instance.due_back is not None


def test_borrow_unavailable_copy_shows_error_and_keeps_state(
    loaned_book_instance, member_user
):
    """REQ-WF-004: Borrowing unavailable copy fails with user feedback."""
    original_borrower = loaned_book_instance.borrower
    client = Client()
    client.force_login(member_user)
    response = client.post(
        reverse("borrow-book", args=[loaned_book_instance.pk]),
        follow=True,
    )
    assert response.status_code == 200
    messages = [str(msg).lower() for msg in response.context["messages"]]
    assert any("unavailable" in msg for msg in messages)

    loaned_book_instance.refresh_from_db()
    assert loaned_book_instance.status == "o"
    assert loaned_book_instance.borrower == original_borrower


def test_return_requires_librarian_permission(loaned_book_instance, member_user):
    """REQ-WF-005: Non-librarian is forbidden from returning copies."""
    client = Client()
    client.force_login(member_user)
    response = client.post(
        reverse("return-book-librarian", args=[loaned_book_instance.pk])
    )
    assert response.status_code == 403


def test_return_get_redirects_without_state_change(loaned_book_instance, librarian_user):
    """Non-POST return request redirects and leaves state unchanged."""
    client = Client()
    client.force_login(librarian_user)
    response = client.get(reverse("return-book-librarian", args=[loaned_book_instance.pk]))
    assert response.status_code == 302
    loaned_book_instance.refresh_from_db()
    assert loaned_book_instance.status == "o"


def test_return_success_resets_fields_and_message(loaned_book_instance, librarian_user):
    """REQ-WF-006/008: Librarian return resets loan fields and shows success flash."""
    client = Client()
    client.force_login(librarian_user)
    response = client.post(
        reverse("return-book-librarian", args=[loaned_book_instance.pk]),
        follow=True,
    )
    assert response.status_code == 200
    messages = [str(msg).lower() for msg in response.context["messages"]]
    assert any("marked as returned" in msg for msg in messages)

    loaned_book_instance.refresh_from_db()
    assert loaned_book_instance.status == "a"
    assert loaned_book_instance.borrower is None
    assert loaned_book_instance.due_back is None


def test_return_already_available_copy_shows_specific_error(
    available_book_instance, librarian_user
):
    """Exception path: returning an available copy surfaces the workflow error."""
    client = Client()
    client.force_login(librarian_user)
    response = client.post(
        reverse("return-book-librarian", args=[available_book_instance.pk]),
        follow=True,
    )
    assert response.status_code == 200
    messages = [str(msg).lower() for msg in response.context["messages"]]
    assert any("only on-loan copies can be marked as returned" in msg for msg in messages)

    available_book_instance.refresh_from_db()
    assert available_book_instance.status == "a"


def test_my_borrowed_requires_login_and_lists_member_loans(
    loaned_book_instance, member_user
):
    """Member borrowed list enforces login and shows current user's loans."""
    unauthenticated_response = Client().get(reverse("my-borrowed"))
    assert unauthenticated_response.status_code == 302

    client = Client()
    client.force_login(member_user)
    response = client.get(reverse("my-borrowed"))
    assert response.status_code == 200
    assert loaned_book_instance.book.title.encode() in response.content


def test_all_borrowed_permission_and_librarian_access(
    loaned_book_instance, member_user, librarian_user
):
    """All borrowed list is forbidden to members and available to librarians."""
    member_client = Client()
    member_client.force_login(member_user)
    forbidden = member_client.get(reverse("all-borrowed"))
    assert forbidden.status_code == 403

    librarian_client = Client()
    librarian_client.force_login(librarian_user)
    allowed = librarian_client.get(reverse("all-borrowed"))
    assert allowed.status_code == 200
    assert loaned_book_instance.book.title.encode() in allowed.content


def test_renewal_requires_librarian_permission(loaned_book_instance, member_user):
    """Renewal endpoint is restricted to librarian users."""
    client = Client()
    client.force_login(member_user)
    response = client.get(reverse("renew-book-librarian", args=[loaned_book_instance.pk]))
    assert response.status_code == 403


def test_renewal_get_prefills_default_date_for_librarian(
    loaned_book_instance, librarian_user
):
    """Librarian GET shows renewal form with a 3-week default date."""
    client = Client()
    client.force_login(librarian_user)
    response = client.get(reverse("renew-book-librarian", args=[loaned_book_instance.pk]))
    assert response.status_code == 200
    assert response.context["form"].initial["renewal_date"] == (
        datetime.date.today() + datetime.timedelta(weeks=3)
    )


def test_renewal_invalid_date_rejected(loaned_book_instance, librarian_user):
    """REQ-WF-012: Past renewal date is rejected with validation message."""
    client = Client()
    client.force_login(librarian_user)
    response = client.post(
        reverse("renew-book-librarian", args=[loaned_book_instance.pk]),
        {"renewal_date": (datetime.date.today() - datetime.timedelta(days=1)).isoformat()},
    )
    assert response.status_code == 200
    assert b"Invalid date" in response.content


def test_renewal_valid_date_updates_due_back_and_redirects(
    loaned_book_instance, librarian_user
):
    """REQ-WF-013: Valid renewal updates due_back and redirects to all-borrowed."""
    valid_date = datetime.date.today() + datetime.timedelta(weeks=2)
    client = Client()
    client.force_login(librarian_user)
    response = client.post(
        reverse("renew-book-librarian", args=[loaned_book_instance.pk]),
        {"renewal_date": valid_date.isoformat()},
    )
    assert response.status_code == 302
    assert reverse("all-borrowed") in response["Location"]

    loaned_book_instance.refresh_from_db()
    assert loaned_book_instance.due_back == valid_date
