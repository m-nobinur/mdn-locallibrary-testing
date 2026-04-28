"""Lean integration tests for Book detail rendering and borrow UI behavior."""

import pytest
from django.test import Client
from django.urls import reverse

pytestmark = [pytest.mark.integration_client, pytest.mark.django_db]


def test_book_detail_renders_core_fields(catalog_book):
    """Book detail page returns 200 and shows key book metadata."""
    response = Client().get(reverse("book-detail", args=[catalog_book.pk]))
    assert response.status_code == 200
    assert catalog_book.title.encode() in response.content
    assert catalog_book.author.last_name.encode() in response.content
    assert catalog_book.isbn.encode() in response.content
    assert catalog_book.summary.encode() in response.content


def test_book_detail_unauthenticated_user_sees_login_to_borrow(
    catalog_book, available_book_instance
):
    """Unauthenticated users should see login CTA, not borrow button."""
    assert available_book_instance.book_id == catalog_book.pk
    response = Client().get(reverse("book-detail", args=[catalog_book.pk]))
    assert response.status_code == 200
    assert b"Log in to borrow this copy." in response.content
    assert b"Borrow this copy" not in response.content


def test_book_detail_authenticated_user_sees_borrow_button(
    catalog_book, available_book_instance, member_user
):
    """Authenticated members should see borrow action for available copies."""
    assert available_book_instance.book_id == catalog_book.pk
    client = Client()
    client.force_login(member_user)
    response = client.get(reverse("book-detail", args=[catalog_book.pk]))
    assert response.status_code == 200
    assert b"Borrow this copy" in response.content
    assert b"Log in to borrow this copy." not in response.content


def test_book_detail_404_for_nonexistent_book():
    """Unknown book id should return 404."""
    response = Client().get(reverse("book-detail", args=[999999]))
    assert response.status_code == 404
