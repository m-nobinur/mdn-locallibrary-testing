"""E2E UI journey: member logs in, searches, and borrows a book."""

import pytest

from tests.fixtures.sample_data import DEFAULT_PASSWORD
from tests.system.pages.book_detail_page import BookDetailPage
from tests.system.pages.borrowed_books_page import BorrowedBooksPage
from tests.system.pages.catalog_page import CatalogPage
from tests.system.pages.login_page import LoginPage

pytestmark = [pytest.mark.e2e_ui, pytest.mark.django_db]


def test_member_can_login_search_and_borrow_book(
    browser,
    system_base_url,
    member_user,
    available_book_instance,
):
    """Member journey: login -> search -> borrow -> verify in my borrowed list."""
    login_page = LoginPage(browser, system_base_url)
    login_page.login(
        username=member_user.username,
        password=DEFAULT_PASSWORD,
        next_path="/catalog/books/",
    )

    catalog_page = CatalogPage(browser, system_base_url)
    catalog_page.search(available_book_instance.book.title)

    catalog_page.open_book_by_title(available_book_instance.book.title)

    detail_page = BookDetailPage(browser, system_base_url)
    detail_page.wait_until_loaded(expected_book_title=available_book_instance.book.title)
    detail_page.borrow_first_available_copy()
    assert detail_page.has_success_message("Borrowed")

    borrowed_page = BorrowedBooksPage(browser, system_base_url)
    borrowed_page.open_my_borrowed()
    assert borrowed_page.has_book_title(available_book_instance.book.title)

    available_book_instance.refresh_from_db()
    assert available_book_instance.status == "o"
    assert available_book_instance.borrower == member_user
