"""Requests-based integration tests for book API endpoints."""

import uuid

import pytest
import requests

from catalog.models import Book
from tests.fixtures.sample_data import DEFAULT_BOOK_SUMMARY
from tests.integration.api.conftest import REQUEST_TIMEOUT_SECONDS

pytestmark = [pytest.mark.integration_api, pytest.mark.django_db(transaction=True)]


def test_books_list_unauthenticated(api_base_url, catalog_book):
    """GET /api/books/ without token is rejected."""
    _ = catalog_book
    response = requests.get(
        f"{api_base_url}/books/",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 401


def test_books_list_authenticated(api_base_url, auth_headers, catalog_book):
    """GET /api/books/ with token returns list payload with expected shape."""
    response = requests.get(
        f"{api_base_url}/books/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload

    book_payload = next((item for item in payload if item["id"] == catalog_book.id), None)
    assert book_payload is not None
    expected_keys = {"id", "title", "author", "summary", "isbn", "genre", "language"}
    assert expected_keys.issubset(book_payload.keys())
    assert isinstance(book_payload["author"], dict)
    assert isinstance(book_payload["genre"], list)
    assert isinstance(book_payload["language"], dict)


def test_book_detail_authenticated(api_base_url, auth_headers, catalog_book):
    """GET /api/books/<id>/ with token returns the expected book payload."""
    response = requests.get(
        f"{api_base_url}/books/{catalog_book.id}/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == catalog_book.id
    assert payload["title"] == catalog_book.title
    assert payload["isbn"] == catalog_book.isbn
    assert payload["author"]["id"] == catalog_book.author_id
    assert payload["language"]["id"] == catalog_book.language_id


def test_book_detail_not_found(api_base_url, auth_headers):
    """GET /api/books/<id>/ returns 404 for a missing resource."""
    response = requests.get(
        f"{api_base_url}/books/999999/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 404


def test_books_search_filter(
    api_base_url,
    auth_headers,
    catalog_author,
    catalog_language,
    catalog_book,
):
    """GET /api/books/?search= returns filtered results for matching titles."""
    other_book = Book.objects.create(
        title="Dracula",
        summary=DEFAULT_BOOK_SUMMARY,
        isbn=f"{uuid.uuid4().int % (10 ** 13):013d}",
        author=catalog_author,
        language=catalog_language,
    )

    response = requests.get(
        f"{api_base_url}/books/?search=frank",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    returned_ids = {item["id"] for item in payload}
    assert catalog_book.id in returned_ids
    assert other_book.id not in returned_ids
