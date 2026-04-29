"""Login/logout interactions for E2E UI tests."""

from urllib.parse import quote

from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    """Page object for Django auth login flow."""

    PATH = "/accounts/login/"

    USERNAME_INPUT = (By.ID, "id_username")
    PASSWORD_INPUT = (By.ID, "id_password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "input[type='submit'][value='login']")
    LOGOUT_FORM = (By.ID, "logout-form")

    def open_login(self, next_path="/catalog/"):
        normalized_next = next_path if next_path.startswith("/") else f"/{next_path}"
        encoded_next = quote(normalized_next, safe="/?=&")
        self.open(f"{self.PATH}?next={encoded_next}")
        self.wait_for_visible(self.USERNAME_INPUT)

    def login(self, username, password, next_path="/catalog/"):
        self.open_login(next_path=next_path)
        self.type(self.USERNAME_INPUT, username)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)
        self.wait_for_visible(self.LOGOUT_FORM)
