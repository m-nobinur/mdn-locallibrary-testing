"""E2E UI journeys for librarian return and member access control."""

import pytest

from tests.system.pages.base_page import BasePage
from tests.system.pages.borrowed_books_page import BorrowedBooksPage

pytestmark = [pytest.mark.e2e_ui, pytest.mark.django_db]


def test_librarian_can_mark_borrowed_copy_as_returned(
    browser,
    system_base_url,
    authenticate_browser,
    librarian_user,
    loaned_book_instance,
):
    """Librarian journey: open borrowed list -> mark returned."""
    authenticate_browser(librarian_user)

    borrowed_page = BorrowedBooksPage(browser, system_base_url)
    borrowed_page.open_all_borrowed(expect_success=True)
    assert borrowed_page.has_book_title(loaned_book_instance.book.title)

    borrowed_page.mark_returned_for_title(loaned_book_instance.book.title)
    assert borrowed_page.has_success_message("marked as returned")

    loaned_book_instance.refresh_from_db()
    assert loaned_book_instance.status == "a"
    assert loaned_book_instance.borrower is None
    assert loaned_book_instance.due_back is None


def test_member_cannot_access_librarian_only_borrowed_area(
    browser,
    system_base_url,
    authenticate_browser,
    member_user,
):
    """Member cannot access /catalog/borrowed/ and should see forbidden response."""
    authenticate_browser(member_user)

    restricted_page = BasePage(browser, system_base_url)
    restricted_page.open("/catalog/borrowed/")
    restricted_page.wait_for_any_text(["403", "Permission denied", "PermissionDenied"])

    assert (
        restricted_page.has_text("403")
        or restricted_page.has_text("Permission denied")
        or restricted_page.has_text("PermissionDenied")
    )
