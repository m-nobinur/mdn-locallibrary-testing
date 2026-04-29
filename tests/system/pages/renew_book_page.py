"""Renew-book form interactions for librarian E2E UI journeys."""

from selenium.webdriver.common.by import By

from .base_page import BasePage


class RenewBookPage(BasePage):
    """Page object for the librarian renew-book form."""

    PATH_TEMPLATE = "/catalog/book/{pk}/renew/"

    PAGE_HEADING = (By.XPATH, "//h1[starts-with(normalize-space(), 'Renew:')]")
    RENEWAL_DATE_INPUT = (By.ID, "id_renewal_date")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "input[type='submit'][value='Submit']")
    ERROR_LIST = (By.CSS_SELECTOR, "ul.errorlist")

    def open_for(self, book_instance_pk):
        self.open(self.PATH_TEMPLATE.format(pk=book_instance_pk))
        self.wait_for_visible(self.PAGE_HEADING)

    def get_default_renewal_date(self):
        return self.wait_for_visible(self.RENEWAL_DATE_INPUT).get_attribute("value")

    def submit_renewal_date(self, iso_date):
        self.type(self.RENEWAL_DATE_INPUT, iso_date)
        self.click(self.SUBMIT_BUTTON)

    def has_validation_error(self, fragment):
        errors = self.browser.find_elements(*self.ERROR_LIST)
        lowered_fragment = fragment.lower()
        return any(lowered_fragment in element.text.lower() for element in errors)
