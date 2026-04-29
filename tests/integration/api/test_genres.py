"""Requests-based integration tests for genre API endpoints."""

import pytest
import requests

from tests.integration.api.conftest import REQUEST_TIMEOUT_SECONDS

pytestmark = [pytest.mark.integration_api, pytest.mark.django_db(transaction=True)]


def test_genres_list_authenticated(api_base_url, auth_headers, catalog_book):
    """GET /api/genres/ with token returns list payload."""
    genre = catalog_book.genre.first()
    assert genre is not None

    response = requests.get(
        f"{api_base_url}/genres/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload

    genre_payload = next((item for item in payload if item["id"] == genre.id), None)
    assert genre_payload is not None
    assert {"id", "name"}.issubset(genre_payload.keys())


def test_genre_detail_authenticated(api_base_url, auth_headers, catalog_book):
    """GET /api/genres/<id>/ with token returns expected genre payload."""
    genre = catalog_book.genre.first()
    assert genre is not None

    response = requests.get(
        f"{api_base_url}/genres/{genre.id}/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == genre.id
    assert payload["name"] == genre.name
