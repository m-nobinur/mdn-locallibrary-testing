import datetime

import pytest
from django.contrib.auth.models import AnonymousUser

from catalog.services import (
    DEFAULT_BORROW_DAYS,
    BorrowWorkflowError,
    borrow_book_copy,
    return_book_copy,
)


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


def test_borrow_book_copy_success_sets_status_borrower_and_due_date(
    available_book_instance,
    member_user,
):
    updated_instance = borrow_book_copy(available_book_instance, member_user)
    available_book_instance.refresh_from_db()

    expected_due_date = datetime.date.today() + datetime.timedelta(
        days=DEFAULT_BORROW_DAYS
    )
    assert updated_instance.pk == available_book_instance.pk
    assert available_book_instance.status == "o"
    assert available_book_instance.borrower == member_user
    assert available_book_instance.due_back == expected_due_date


def test_borrow_book_copy_rejects_unavailable_copy(
    available_book_instance, member_user
):
    available_book_instance.status = "o"
    available_book_instance.save(update_fields=["status"])

    with pytest.raises(BorrowWorkflowError, match="currently unavailable"):
        borrow_book_copy(available_book_instance, member_user)


def test_borrow_book_copy_requires_authenticated_borrower(available_book_instance):
    with pytest.raises(BorrowWorkflowError, match="logged in"):
        borrow_book_copy(available_book_instance, AnonymousUser())


def test_borrow_book_copy_rejects_invalid_borrow_duration(
    available_book_instance,
    member_user,
):
    with pytest.raises(BorrowWorkflowError, match="at least one day"):
        borrow_book_copy(available_book_instance, member_user, borrow_days=0)


def test_return_book_copy_success_resets_loan_fields(loaned_book_instance):
    updated_instance = return_book_copy(loaned_book_instance)
    loaned_book_instance.refresh_from_db()

    assert updated_instance.pk == loaned_book_instance.pk
    assert loaned_book_instance.status == "a"
    assert loaned_book_instance.borrower is None
    assert loaned_book_instance.due_back is None


def test_return_book_copy_rejects_non_loan_status(available_book_instance):
    with pytest.raises(BorrowWorkflowError, match="Only on-loan copies"):
        return_book_copy(available_book_instance)
