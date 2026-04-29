"""Requests-based integration tests for book-instance API endpoints."""

import pytest
import requests

from tests.integration.api.conftest import REQUEST_TIMEOUT_SECONDS

pytestmark = [pytest.mark.integration_api, pytest.mark.django_db(transaction=True)]


def test_book_instances_list_authenticated(
    api_base_url,
    auth_headers,
    available_book_instance,
):
    """GET /api/book-instances/ with token returns list payload."""
    response = requests.get(
        f"{api_base_url}/book-instances/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload

    instance_payload = next(
        (item for item in payload if item["id"] == str(available_book_instance.id)),
        None,
    )
    assert instance_payload is not None
    expected_keys = {"id", "book", "imprint", "due_back", "status", "borrower", "is_overdue"}
    assert expected_keys.issubset(instance_payload.keys())


def test_book_instances_status_filter(
    api_base_url,
    auth_headers,
    available_book_instance,
    loaned_book_instance,
):
    """GET /api/book-instances/?status=a returns only available copies."""
    _ = loaned_book_instance
    response = requests.get(
        f"{api_base_url}/book-instances/?status=a",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload
    returned_ids = {item["id"] for item in payload}
    assert str(available_book_instance.id) in returned_ids
    assert all(item["status"] == "a" for item in payload)


def test_book_instance_detail_authenticated(
    api_base_url,
    auth_headers,
    available_book_instance,
):
    """GET /api/book-instances/<id>/ with token returns expected fields."""
    response = requests.get(
        f"{api_base_url}/book-instances/{available_book_instance.id}/",
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    payload = response.json()
    expected_keys = {"id", "book", "imprint", "due_back", "status", "borrower", "is_overdue"}
    assert expected_keys.issubset(payload.keys())
    assert payload["id"] == str(available_book_instance.id)
    assert payload["book"] == str(available_book_instance.book)
    assert payload["imprint"] == available_book_instance.imprint
    assert payload["status"] == available_book_instance.status
    assert payload["borrower"] is None
    assert payload["is_overdue"] is False
