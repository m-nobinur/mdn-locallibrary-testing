"""Lean integration tests for catalog search behavior (REQ-WF-001)."""

import uuid

import pytest
from django.test import Client
from django.urls import reverse

from catalog.models import Book
from tests.fixtures.sample_data import DEFAULT_BOOK_SUMMARY

pytestmark = [pytest.mark.integration_client, pytest.mark.django_db]


def test_book_list_without_query_returns_all_books(
    catalog_book, catalog_author, catalog_language
):
    """Book list returns 200 and renders all books when no query is provided."""
    other_book = Book.objects.create(
        title="Dracula",
        summary=DEFAULT_BOOK_SUMMARY,
        isbn=f"{uuid.uuid4().int % (10 ** 13):013d}",
        author=catalog_author,
        language=catalog_language,
    )
    response = Client().get(reverse("books"))
    assert response.status_code == 200
    assert response.context["search_query"] == ""
    assert catalog_book.title.encode() in response.content
    assert other_book.title.encode() in response.content


def test_book_list_search_filters_case_insensitively(
    catalog_book, catalog_author, catalog_language
):
    """Search query filters by title using icontains and excludes non-matches."""
    other_book = Book.objects.create(
        title="Dracula",
        summary=DEFAULT_BOOK_SUMMARY,
        isbn=f"{uuid.uuid4().int % (10 ** 13):013d}",
        author=catalog_author,
        language=catalog_language,
    )
    response = Client().get(reverse("books"), {"q": "FRANK"})
    assert response.status_code == 200
    assert response.context["search_query"] == "FRANK"
    assert b'Showing matches for "FRANK".' in response.content
    assert catalog_book.title.encode() in response.content
    assert other_book.title.encode() not in response.content


def test_book_list_search_no_match_shows_empty_state(catalog_book):
    """A non-matching query returns an empty list message."""
    response = Client().get(reverse("books"), {"q": "nonexistent-title-xyz"})
    assert response.status_code == 200
    assert b"There are no books in the library." in response.content
    assert catalog_book.title.encode() not in response.content


def test_book_list_uses_book_list_template():
    """Book list view renders catalog/book_list.html."""
    response = Client().get(reverse("books"))
    template_names = [template.name for template in response.templates]
    assert "catalog/book_list.html" in template_names
