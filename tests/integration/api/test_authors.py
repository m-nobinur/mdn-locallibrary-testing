"""Requests-based integration tests for author API endpoints."""

import pytest
import requests

from tests.integration.api.conftest import REQUEST_TIMEOUT_SECONDS

pytestmark = [pytest.mark.integration_api, pytest.mark.django_db(transaction=True)]


def test_authors_list_authenticated(api_base_url, auth_headers, catalog_author):
    """GET /api/authors/ with token returns list payload with expected fields."""
    response = requests.get(
        f"{api_base_url}/authors/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload

    author_payload = next((item for item in payload if item["id"] == catalog_author.id), None)
    assert author_payload is not None
    expected_keys = {"id", "first_name", "last_name", "date_of_birth", "date_of_death"}
    assert expected_keys.issubset(author_payload.keys())


def test_author_detail_authenticated(api_base_url, auth_headers, catalog_author):
    """GET /api/authors/<id>/ with token returns the expected author payload."""
    response = requests.get(
        f"{api_base_url}/authors/{catalog_author.id}/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    expected_keys = {"id", "first_name", "last_name", "date_of_birth", "date_of_death"}
    assert expected_keys.issubset(payload.keys())
    assert payload["id"] == catalog_author.id
    assert payload["first_name"] == catalog_author.first_name
    assert payload["last_name"] == catalog_author.last_name
