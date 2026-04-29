"""E2E UI journey: anonymous visitor browses the public catalog."""

import pytest

from tests.system.pages.base_page import BasePage

pytestmark = [pytest.mark.e2e_ui, pytest.mark.django_db]


def test_anonymous_visitor_can_browse_public_catalog_pages(
    browser,
    system_base_url,
    available_book_instance,
):
    """Anonymous browse: home -> books -> book detail -> authors -> genres -> languages."""
    catalog_book = available_book_instance.book
    catalog_author = catalog_book.author
    expected_genre_name = catalog_book.genre.first().name
    expected_language_name = catalog_book.language.name

    page = BasePage(browser, system_base_url)

    page.open("/catalog/")
    page.wait_for_text("Local Library Home")
    assert page.has_text("Dynamic content")

    page.open("/catalog/books/")
    page.wait_for_text("Book List")
    assert page.has_text(catalog_book.title)

    page.open(catalog_book.get_absolute_url())
    page.wait_for_text(f"Title: {catalog_book.title}")
    assert page.has_text("Log in to borrow this copy.")

    page.open("/catalog/authors/")
    page.wait_for_text("Author List")
    assert page.has_text(catalog_author.last_name)

    page.open("/catalog/genres/")
    page.wait_for_text("Genre List")
    assert page.has_text(expected_genre_name)

    page.open("/catalog/languages/")
    page.wait_for_text("Language List")
    assert page.has_text(expected_language_name)
