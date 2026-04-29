"""Shared fixtures for Requests-based API integration tests."""

from urllib.parse import urlparse

import pytest
import requests

from tests.fixtures.sample_data import DEFAULT_PASSWORD

REQUEST_TIMEOUT_SECONDS = 5


@pytest.fixture(name="api_base_url")
def fixture_api_base_url(live_server, settings):
    """Return the API base URL for the live Django test server."""
    live_server_host = urlparse(live_server.url).hostname
    if live_server_host and live_server_host not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append(live_server_host)
    return f"{live_server.url}/api"


@pytest.fixture(name="api_user")
def fixture_api_user(django_user_model):
    """Create a dedicated user for API token authentication tests."""
    return django_user_model.objects.create_user(
        username="api-integration-user",
        password=DEFAULT_PASSWORD,
    )


@pytest.fixture(name="api_auth_token")
def fixture_api_auth_token(api_base_url, api_user):
    """Obtain a valid token using the real API authentication endpoint."""
    response = requests.post(
        f"{api_base_url}/auth/token/",
        data={"username": api_user.username, "password": DEFAULT_PASSWORD},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["token"]


@pytest.fixture(name="auth_headers")
def fixture_auth_headers(api_auth_token):
    """Authorization header for authenticated API requests."""
    return {"Authorization": f"Token {api_auth_token}"}
