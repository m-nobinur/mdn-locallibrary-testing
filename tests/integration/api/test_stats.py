"""Requests-based integration tests for stats API endpoint."""

import pytest
import requests

from catalog.models import Author, Book, BookInstance, Genre, Language
from tests.integration.api.conftest import REQUEST_TIMEOUT_SECONDS

pytestmark = [pytest.mark.integration_api, pytest.mark.django_db(transaction=True)]


def test_catalog_stats_authenticated(
    api_base_url,
    auth_headers,
    catalog_author,
    catalog_book,
    catalog_language,
    available_book_instance,
    loaned_book_instance,
):
    """GET /api/stats/ with token returns expected count keys and values."""
    _ = (
        catalog_author,
        catalog_book,
        catalog_language,
        available_book_instance,
        loaned_book_instance,
    )
    response = requests.get(
        f"{api_base_url}/stats/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    expected_keys = {
        "total_books",
        "total_book_instances",
        "available_book_instances",
        "on_loan_book_instances",
        "total_authors",
        "total_genres",
        "total_languages",
    }
    assert expected_keys.issubset(payload.keys())

    assert payload["total_books"] == Book.objects.count()
    assert payload["total_book_instances"] == BookInstance.objects.count()
    assert payload["available_book_instances"] == BookInstance.objects.filter(status="a").count()
    assert payload["on_loan_book_instances"] == BookInstance.objects.filter(status="o").count()
    assert payload["total_authors"] == Author.objects.count()
    assert payload["total_genres"] == Genre.objects.count()
    assert payload["total_languages"] == Language.objects.count()


def test_catalog_stats_unauthenticated(api_base_url, catalog_book):
    """GET /api/stats/ without token is rejected."""
    _ = catalog_book
    response = requests.get(
        f"{api_base_url}/stats/",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 401
