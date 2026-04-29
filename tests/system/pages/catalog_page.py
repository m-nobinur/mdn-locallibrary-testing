"""Catalog search/list interactions for E2E UI tests."""

from selenium.webdriver.common.by import By

from .base_page import BasePage


class CatalogPage(BasePage):
    """Page object for the catalog book list/search page."""

    PATH = "/catalog/books/"

    BOOK_LIST_HEADING = (By.XPATH, "//h1[normalize-space()='Book List']")
    SEARCH_INPUT = (By.ID, "book-search")
    SEARCH_BUTTON = (By.XPATH, "//button[normalize-space()='Search']")

    def open_page(self):
        self.open(self.PATH)
        self.wait_for_visible(self.BOOK_LIST_HEADING)

    def search(self, query):
        if self.current_path != self.PATH:
            self.open_page()
        self.type(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_text(f'Showing matches for "{query}".')

    def open_book_by_title(self, title):
        self.click((By.LINK_TEXT, title))
