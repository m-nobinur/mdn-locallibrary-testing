import datetime
import uuid

import pytest
from django.contrib.auth import get_user_model

from catalog.models import Author, Book, BookInstance, Genre, Language
from tests.fixtures.sample_data import (
    DEFAULT_BOOK_IMPRINT,
    DEFAULT_BOOK_SUMMARY,
    DEFAULT_PASSWORD,
)


def _unique_13_digit_number():
    return f"{uuid.uuid4().int % (10**13):013d}"


@pytest.fixture(name="member_user")
def fixture_member_user():
    user_model = get_user_model()
    return user_model.objects.create_user(
        username="member-user",
        password=DEFAULT_PASSWORD,
    )


@pytest.fixture(name="catalog_author")
def fixture_catalog_author():
    return Author.objects.create(first_name="Mary", last_name="Shelley")


@pytest.fixture(name="catalog_language")
def fixture_catalog_language():
    return Language.objects.create(name="English")


@pytest.fixture(name="catalog_book")
def fixture_catalog_book(catalog_author, catalog_language):
    book = Book.objects.create(
        title="Frankenstein",
        summary=DEFAULT_BOOK_SUMMARY,
        isbn=_unique_13_digit_number(),
        author=catalog_author,
        language=catalog_language,
    )
    genre = Genre.objects.create(name="Gothic")
    book.genre.add(genre)
    return book


@pytest.fixture(name="available_book_instance")
def fixture_available_book_instance(catalog_book):
    return BookInstance.objects.create(
        book=catalog_book,
        imprint=DEFAULT_BOOK_IMPRINT,
        status="a",
    )


@pytest.fixture(name="loaned_book_instance")
def fixture_loaned_book_instance(catalog_book, member_user):
    return BookInstance.objects.create(
        book=catalog_book,
        imprint=DEFAULT_BOOK_IMPRINT,
        status="o",
        borrower=member_user,
        due_back=datetime.date.today() + datetime.timedelta(days=7),
    )
