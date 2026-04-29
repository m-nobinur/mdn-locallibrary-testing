"""Book-detail interactions for borrow journey E2E UI tests."""

from selenium.webdriver.common.by import By

from .base_page import BasePage


class BookDetailPage(BasePage):
    """Page object for book detail and borrow actions."""

    PATH_TEMPLATE = "/catalog/book/{pk}"

    PAGE_TITLE = (By.TAG_NAME, "h1")
    BORROW_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(), 'Borrow this copy')]",
    )
    SUCCESS_ALERT = (By.CSS_SELECTOR, ".alert.alert-success")
    ERROR_ALERT = (By.CSS_SELECTOR, ".alert.alert-danger")

    def open_for(self, book_pk):
        self.open(self.PATH_TEMPLATE.format(pk=book_pk))
        self.wait_for_visible(self.PAGE_TITLE)

    def wait_until_loaded(self, expected_book_title=None):
        self.wait_for_visible(self.PAGE_TITLE)
        if expected_book_title:
            self.wait_for_text(expected_book_title)

    def borrow_first_available_copy(self):
        self.click(self.BORROW_BUTTON)
        self.wait_for_visible(self.SUCCESS_ALERT)

    def click_borrow_button(self):
        self.click(self.BORROW_BUTTON)

    def has_success_message(self, fragment):
        return self.has_alert_message(fragment)

    def has_error_message(self, fragment):
        return self.has_alert_message(fragment)
