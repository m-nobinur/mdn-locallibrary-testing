"""Base page object helpers used by Selenium E2E UI tests."""

from urllib.parse import urlparse

from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Shared browser helpers for robust page-object interactions."""

    DEFAULT_TIMEOUT_SECONDS = 10

    def __init__(self, browser, base_url):
        self.browser = browser
        self.base_url = base_url.rstrip("/")

    def open(self, path):
        if path.startswith("http://") or path.startswith("https://"):
            target_url = path
        else:
            normalized_path = path if path.startswith("/") else f"/{path}"
            target_url = f"{self.base_url}{normalized_path}"
        self.browser.get(target_url)

    def wait_for_visible(self, locator, timeout=None):
        wait_timeout = (
            timeout if timeout is not None else self.DEFAULT_TIMEOUT_SECONDS
        )
        return WebDriverWait(self.browser, wait_timeout).until(
            expected.visibility_of_element_located(locator)
        )

    def wait_for_clickable(self, locator, timeout=None):
        wait_timeout = (
            timeout if timeout is not None else self.DEFAULT_TIMEOUT_SECONDS
        )
        return WebDriverWait(self.browser, wait_timeout).until(
            expected.element_to_be_clickable(locator)
        )

    def click(self, locator):
        self.wait_for_clickable(locator).click()

    def type(self, locator, value, clear=True):
        element = self.wait_for_visible(locator)
        if clear:
            element.clear()
        element.send_keys(value)

    def _get_body_text(self):
        try:
            return self.browser.find_element(By.TAG_NAME, "body").text
        except (StaleElementReferenceException, WebDriverException):
            try:
                return self.browser.page_source
            except WebDriverException:
                return ""

    def wait_for_text(self, text, timeout=None):
        wait_timeout = (
            timeout if timeout is not None else self.DEFAULT_TIMEOUT_SECONDS
        )
        WebDriverWait(self.browser, wait_timeout).until(
            lambda driver: text in self._get_body_text()
        )

    def wait_for_any_text(self, fragments, timeout=None):
        wait_timeout = (
            timeout if timeout is not None else self.DEFAULT_TIMEOUT_SECONDS
        )
        WebDriverWait(self.browser, wait_timeout).until(
            lambda driver: any(fragment in self._get_body_text() for fragment in fragments)
        )

    def has_text(self, text):
        return text in self._get_body_text()

    @staticmethod
    def xpath_literal(value):
        """Return an XPath-safe string literal for arbitrary text."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"

    def has_alert_message(self, fragment):
        alerts = self.browser.find_elements(By.CSS_SELECTOR, ".alert")
        lowered_fragment = fragment.lower()
        return any(lowered_fragment in alert.text.lower() for alert in alerts)

    @property
    def current_path(self):
        """Return the current URL path (without query string)."""
        return urlparse(self.browser.current_url).path
