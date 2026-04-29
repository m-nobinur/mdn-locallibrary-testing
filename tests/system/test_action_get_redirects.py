"""E2E UI tests: borrow/return action endpoints reject browser GETs.

These journeys cover the defensive branches that redirect a browser away from
state-mutating action URLs when the request is not a POST. They also exercise
the `_safe_next_url` fallback path because no `next` parameter is provided.
"""

import pytest

from tests.system.pages.base_page import BasePage
from tests.system.pages.borrowed_books_page import BorrowedBooksPage

pytestmark = [pytest.mark.e2e_ui, pytest.mark.django_db]


def test_member_borrow_link_via_get_redirects_without_state_change(
    browser,
    system_base_url,
    authenticate_browser,
    member_user,
    available_book_instance,
):
    """A member typing the borrow URL into the address bar must be redirected
    to their borrowed-books list without any state change."""
    authenticate_browser(member_user)

    page = BasePage(browser, system_base_url)
    page.open(f"/catalog/bookinstance/{available_book_instance.pk}/borrow/")

    borrowed_page = BorrowedBooksPage(browser, system_base_url)
    borrowed_page.wait_for_visible(BorrowedBooksPage.MY_BORROWED_HEADING)
    assert page.current_path == BorrowedBooksPage.MY_BORROWED_PATH

    available_book_instance.refresh_from_db()
    assert available_book_instance.status == "a"
    assert available_book_instance.borrower is None


def test_librarian_return_link_via_get_redirects_without_state_change(
    browser,
    system_base_url,
    authenticate_browser,
    librarian_user,
    loaned_book_instance,
):
    """A librarian opening the return URL with GET must be redirected to the
    all-borrowed list without changing the loan."""
    authenticate_browser(librarian_user)

    page = BasePage(browser, system_base_url)
    page.open(f"/catalog/bookinstance/{loaned_book_instance.pk}/return/")

    borrowed_page = BorrowedBooksPage(browser, system_base_url)
    borrowed_page.wait_for_visible(BorrowedBooksPage.ALL_BORROWED_HEADING)
    assert page.current_path == BorrowedBooksPage.ALL_BORROWED_PATH

    original_borrower_id = loaned_book_instance.borrower_id
    loaned_book_instance.refresh_from_db()
    assert loaned_book_instance.status == "o"
    assert loaned_book_instance.borrower_id == original_borrower_id
    assert loaned_book_instance.due_back is not None
