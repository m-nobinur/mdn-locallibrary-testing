"""Requests-based integration tests for language API endpoints."""

import pytest
import requests

from tests.integration.api.conftest import REQUEST_TIMEOUT_SECONDS

pytestmark = [pytest.mark.integration_api, pytest.mark.django_db(transaction=True)]


def test_languages_list_authenticated(api_base_url, auth_headers, catalog_language):
    """GET /api/languages/ with token returns list payload."""
    response = requests.get(
        f"{api_base_url}/languages/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload

    language_payload = next(
        (item for item in payload if item["id"] == catalog_language.id),
        None,
    )
    assert language_payload is not None
    assert {"id", "name"}.issubset(language_payload.keys())


def test_language_detail_authenticated(api_base_url, auth_headers, catalog_language):
    """GET /api/languages/<id>/ with token returns expected language payload."""
    response = requests.get(
        f"{api_base_url}/languages/{catalog_language.id}/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == catalog_language.id
    assert payload["name"] == catalog_language.name
