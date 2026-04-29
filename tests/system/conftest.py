"""Fixtures for Selenium-based E2E UI tests."""

import os
from urllib.parse import urlparse

import pytest
from django.conf import settings as django_settings
from django.test import Client
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

SYSTEM_TEST_ENV_VAR = "RUN_SYSTEM_TESTS"
HEADLESS_ENV_VAR = "SYSTEM_TEST_HEADLESS"


def _is_truthy(value):
    return value.lower() in {"1", "true", "yes", "on"}


@pytest.fixture(scope="session", autouse=True)
def require_system_tests_enabled():
    """Skip this module unless RUN_SYSTEM_TESTS=1 is explicitly set."""
    if not _is_truthy(os.getenv(SYSTEM_TEST_ENV_VAR, "")):
        pytest.skip(
            "E2E UI tests are disabled. Set RUN_SYSTEM_TESTS=1 to execute browser journeys."
        )


@pytest.fixture(name="system_base_url")
def fixture_system_base_url(live_server, settings):
    """Return the base URL for the live Django test server."""
    live_server_host = urlparse(live_server.url).hostname
    if live_server_host and live_server_host not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append(live_server_host)
    return live_server.url


@pytest.fixture(name="browser", scope="session")
def fixture_browser():
    """Create a single Chrome WebDriver session reused across E2E UI tests.

    A session-scoped browser is significantly faster than a per-test one in
    headed mode (no window churn between tests) and lets Selenium Manager
    resolve the chromedriver binary just once. Per-test isolation is
    re-established by `reset_browser_state` which clears cookies between
    tests.
    """
    headed = not _is_truthy(os.getenv(HEADLESS_ENV_VAR, "1"))

    options = Options()
    if not headed:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")

    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as exc:
        pytest.skip(f"Unable to start Chrome WebDriver for E2E UI tests: {exc}")

    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture(autouse=True)
def reset_browser_state(browser):
    """Reset browser state between tests for isolation."""
    yield

    try:
        browser.delete_all_cookies()
        browser.execute_script(
            "window.localStorage.clear(); window.sessionStorage.clear();"
        )
    except WebDriverException:
        pass


@pytest.fixture(name="authenticate_browser")
def fixture_authenticate_browser(browser, system_base_url):
    """Programmatically log a user in and attach the session cookie to Selenium.

    Use this for journeys where the login UI itself is not under test. It mints
    a Django session via `Client.force_login` and injects that session cookie
    into Selenium, bypassing the login form to keep the suite fast.
    """
    def _authenticate(user):
        client = Client()
        client.force_login(user)
        session_cookie = client.cookies[django_settings.SESSION_COOKIE_NAME]

        # Selenium can only set cookies for the currently loaded origin, so
        # navigate to the live server first.
        browser.get(system_base_url)
        browser.add_cookie(
            {
                "name": django_settings.SESSION_COOKIE_NAME,
                "value": session_cookie.value,
                "path": "/",
            }
        )
        return user

    return _authenticate
