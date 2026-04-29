"""E2E UI tests: borrow/return workflow error paths.

These journeys cover the defensive server-side error handlers that fire when
the action endpoints are reached with state that the UI normally hides:

- a member submits the borrow form for a copy that became unavailable between
  page load and click (covers the `BorrowWorkflowError` branch in
  `borrow_book`)
- a librarian submits the return form for a copy that was returned between
  page load and click (covers the `BorrowWorkflowError` branch in
  `return_book_librarian`)
- an editor bypasses the delete-confirmation gate via a direct POST to a book
  that has copies, exercising the `RestrictedError` safety net in
  `BookDelete.form_valid`
"""

import datetime

import pytest
from selenium.webdriver.common.by import By

from tests.system.pages.book_detail_page import BookDetailPage
from tests.system.pages.borrowed_books_page import BorrowedBooksPage

pytestmark = [pytest.mark.e2e_ui, pytest.mark.django_db]


def _submit_post_with_csrf(browser, url):
    """Submit a same-origin POST via JS using the current CSRF cookie."""
    csrf_cookie = browser.get_cookie("csrftoken")
    assert csrf_cookie is not None, "Expected CSRF cookie before defense-in-depth POST"

    script = (
        "const form = document.createElement('form');"
        "form.method = 'POST';"
        "form.action = arguments[0];"
        "const tokenInput = document.createElement('input');"
        "tokenInput.type = 'hidden';"
        "tokenInput.name = 'csrfmiddlewaretoken';"
        "tokenInput.value = arguments[1];"
        "form.appendChild(tokenInput);"
        "document.body.appendChild(form);"
        "form.submit();"
    )
    browser.execute_script(script, url, csrf_cookie["value"])


def test_member_borrow_form_handles_concurrent_unavailability(
    browser,
    system_base_url,
    authenticate_browser,
    member_user,
    librarian_user,
    available_book_instance,
):
    """Race condition: member loads detail with copy available, copy gets borrowed
    by someone else, then member clicks Borrow → server returns a flash error
    via the BorrowWorkflowError branch in borrow_book."""
    authenticate_browser(member_user)

    detail_page = BookDetailPage(browser, system_base_url)
    detail_page.open_for(available_book_instance.book.pk)
    detail_page.wait_until_loaded(
        expected_book_title=available_book_instance.book.title
    )

    # Simulate a concurrent borrow by another user mutating the DB after page load.
    available_book_instance.status = "o"
    available_book_instance.borrower = librarian_user
    available_book_instance.due_back = datetime.date.today() + datetime.timedelta(
        days=14
    )
    available_book_instance.save(update_fields=["status", "borrower", "due_back"])

    detail_page.click_borrow_button()
    detail_page.wait_for_visible(BookDetailPage.ERROR_ALERT)

    assert detail_page.has_error_message("currently unavailable")

    available_book_instance.refresh_from_db()
    assert available_book_instance.status == "o"
    assert available_book_instance.borrower == librarian_user


def test_librarian_return_form_handles_concurrent_return(
    browser,
    system_base_url,
    authenticate_browser,
    librarian_user,
    loaned_book_instance,
):
    """Race condition: librarian loads all-borrowed, copy is concurrently
    returned, then librarian clicks Mark returned → server returns a flash
    error via the BorrowWorkflowError branch in return_book_librarian."""
    authenticate_browser(librarian_user)

    borrowed_page = BorrowedBooksPage(browser, system_base_url)
    borrowed_page.open_all_borrowed(expect_success=True)
    assert borrowed_page.has_book_title(loaned_book_instance.book.title)

    # Simulate the copy being returned by another librarian after page load.
    loaned_book_instance.status = "a"
    loaned_book_instance.borrower = None
    loaned_book_instance.due_back = None
    loaned_book_instance.save(update_fields=["status", "borrower", "due_back"])

    borrowed_page.click_mark_returned_for_title(loaned_book_instance.book.title)
    borrowed_page.wait_for_visible(BorrowedBooksPage.ERROR_ALERT)

    assert borrowed_page.has_error_message("Only on-loan copies")

    loaned_book_instance.refresh_from_db()
    assert loaned_book_instance.status == "a"
    assert loaned_book_instance.borrower is None
    assert loaned_book_instance.due_back is None


def test_book_delete_server_blocks_when_copies_exist_via_direct_post(
    browser,
    system_base_url,
    authenticate_browser,
    editor_user,
    available_book_instance,
):
    """Defense-in-depth: an editor bypasses the gated delete-confirmation
    template by submitting a direct POST. The server must catch the
    RestrictedError, refuse the deletion, surface a flash message, and
    keep the book in place."""
    authenticate_browser(editor_user)

    book = available_book_instance.book
    delete_path = f"/catalog/book/{book.pk}/delete/"

    detail_page = BookDetailPage(browser, system_base_url)
    detail_page.open_for(book.pk)
    detail_page.wait_until_loaded(expected_book_title=book.title)

    delete_url = f"{system_base_url.rstrip('/')}{delete_path}"
    _submit_post_with_csrf(browser, delete_url)

    detail_page.wait_for_visible((By.CSS_SELECTOR, ".alert.alert-danger"))
    assert detail_page.current_path == delete_path
    assert (
        detail_page.has_text("RestrictedError")
        or detail_page.has_text("Cannot delete")
        or detail_page.has_text("protect related objects")
    )

    available_book_instance.refresh_from_db()
    assert available_book_instance.book_id == book.pk
    book.refresh_from_db()
    assert book.pk is not None
