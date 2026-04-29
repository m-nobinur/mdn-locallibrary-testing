"""E2E UI journey: librarian renews and validates the renew form."""

import datetime

import pytest

from tests.system.pages.borrowed_books_page import BorrowedBooksPage
from tests.system.pages.renew_book_page import RenewBookPage

pytestmark = [pytest.mark.e2e_ui, pytest.mark.django_db]


def test_librarian_can_renew_borrowed_copy_with_valid_date(
    browser,
    system_base_url,
    authenticate_browser,
    librarian_user,
    loaned_book_instance,
):
    """Librarian opens the all-borrowed list, follows the Renew link, and submits a valid date."""
    authenticate_browser(librarian_user)

    borrowed_page = BorrowedBooksPage(browser, system_base_url)
    borrowed_page.open_all_borrowed(expect_success=True)
    assert borrowed_page.has_book_title(loaned_book_instance.book.title)

    renew_page = RenewBookPage(browser, system_base_url)
    renew_page.open_for(loaned_book_instance.pk)
    expected_default = (
        datetime.date.today() + datetime.timedelta(weeks=3)
    ).isoformat()
    assert renew_page.get_default_renewal_date() == expected_default

    valid_renewal_date = datetime.date.today() + datetime.timedelta(weeks=2)
    renew_page.submit_renewal_date(valid_renewal_date.isoformat())

    borrowed_page.wait_for_visible(BorrowedBooksPage.ALL_BORROWED_HEADING)
    assert browser.current_url.endswith("/catalog/borrowed/")

    loaned_book_instance.refresh_from_db()
    assert loaned_book_instance.due_back == valid_renewal_date


def test_librarian_renew_form_rejects_far_future_date(
    browser,
    system_base_url,
    authenticate_browser,
    librarian_user,
    loaned_book_instance,
):
    """Submitting a date more than four weeks ahead must re-render the form with an error."""
    authenticate_browser(librarian_user)

    original_due_back = loaned_book_instance.due_back

    renew_page = RenewBookPage(browser, system_base_url)
    renew_page.open_for(loaned_book_instance.pk)

    far_future = datetime.date.today() + datetime.timedelta(weeks=8)
    renew_page.submit_renewal_date(far_future.isoformat())

    renew_page.wait_for_visible(RenewBookPage.PAGE_HEADING)
    assert renew_page.has_validation_error("more than 4 weeks ahead")

    loaned_book_instance.refresh_from_db()
    assert loaned_book_instance.due_back == original_due_back
