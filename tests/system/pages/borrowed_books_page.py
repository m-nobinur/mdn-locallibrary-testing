"""Borrowed-books page interactions for member and librarian journeys."""

from selenium.webdriver.common.by import By

from .base_page import BasePage


class BorrowedBooksPage(BasePage):
    """Page object for member and librarian borrowed-list pages."""

    MY_BORROWED_PATH = "/catalog/mybooks/"
    ALL_BORROWED_PATH = "/catalog/borrowed/"

    MY_BORROWED_HEADING = (By.XPATH, "//h1[normalize-space()='Borrowed books']")
    ALL_BORROWED_HEADING = (By.XPATH, "//h1[normalize-space()='All Borrowed Books']")
    ERROR_ALERT = (By.CSS_SELECTOR, ".alert.alert-danger")

    def open_my_borrowed(self):
        self.open(self.MY_BORROWED_PATH)
        self.wait_for_visible(self.MY_BORROWED_HEADING)

    def open_all_borrowed(self, expect_success=True):
        self.open(self.ALL_BORROWED_PATH)
        if expect_success:
            self.wait_for_visible(self.ALL_BORROWED_HEADING)

    def has_book_title(self, title):
        links = self.browser.find_elements(By.LINK_TEXT, title)
        return any(link.is_displayed() for link in links)

    def _mark_returned_button_locator(self, title):
        title_literal = self.xpath_literal(title)
        return (
            By.XPATH,
            f"//li[a[normalize-space()={title_literal}]]//button[contains(normalize-space(), 'Mark returned')]",
        )

    def mark_returned_for_title(self, title):
        self.click(self._mark_returned_button_locator(title))
        self.wait_for_visible((By.CSS_SELECTOR, ".alert.alert-success"))

    def click_mark_returned_for_title(self, title):
        self.click(self._mark_returned_button_locator(title))

    def has_success_message(self, fragment):
        return self.has_alert_message(fragment)

    def has_error_message(self, fragment):
        return self.has_alert_message(fragment)
