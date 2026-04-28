"""Requests-based integration tests for API token authentication."""

import pytest
import requests

from tests.fixtures.sample_data import DEFAULT_PASSWORD
from tests.integration.api.conftest import REQUEST_TIMEOUT_SECONDS

pytestmark = [pytest.mark.integration_api, pytest.mark.django_db(transaction=True)]


def test_obtain_token_with_valid_credentials(api_base_url, api_user):
    """POST /api/auth/token/ returns 200 with a token for valid credentials."""
    response = requests.post(
        f"{api_base_url}/auth/token/",
        data={"username": api_user.username, "password": DEFAULT_PASSWORD},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert "token" in payload
    assert isinstance(payload["token"], str)
    assert payload["token"]


def test_obtain_token_with_invalid_credentials(api_base_url, api_user):
    """POST /api/auth/token/ returns 400 for invalid credentials."""
    response = requests.post(
        f"{api_base_url}/auth/token/",
        data={"username": api_user.username, "password": "wrong-password"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 400
    payload = response.json()
    assert "token" not in payload
    assert "non_field_errors" in payload
