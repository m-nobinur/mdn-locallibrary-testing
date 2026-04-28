import datetime
import sys
import uuid
from copy import copy
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.test import client as django_test_client


from catalog.models import Author, Book, BookInstance, Genre, Language
from tests.fixtures.sample_data import (
    DEFAULT_BOOK_IMPRINT,
    DEFAULT_BOOK_SUMMARY,
    DEFAULT_PASSWORD,
)

_PY314_PATCH_STATE = {"store_rendered_templates_patched": False}


def pytest_configure():
    """Apply runtime compatibility patches needed by this test environment."""
    if sys.version_info < (3, 14):
        return

    if _PY314_PATCH_STATE["store_rendered_templates_patched"]:
        return

    def store_rendered_templates_compat(
        store, signal, sender, template, context, **kwargs
    ):
        """Fallback to raw context when Django's shallow copy fails on Python 3.14."""
        _ = (signal, sender, kwargs)
        store.setdefault("templates", []).append(template)
        if "context" not in store:
            store["context"] = django_test_client.ContextList()

        try:
            store["context"].append(copy(context))
        except AttributeError:
            if hasattr(context, "flatten"):
                store["context"].append(context.flatten())
            elif hasattr(context, "dicts"):
                flattened_context = {}
                for layer in context.dicts:
                    flattened_context.update(layer)
                store["context"].append(flattened_context)
            else:
                store["context"].append(context)

    django_test_client.store_rendered_templates = store_rendered_templates_compat
    _PY314_PATCH_STATE["store_rendered_templates_patched"] = True


def _unique_13_digit_number():
    return f"{uuid.uuid4().int % (10**13):013d}"


@pytest.fixture(autouse=True)
def configure_test_staticfiles_storage(settings):
    """Use non-manifest staticfiles storage so template rendering works in tests."""
    storages = dict(settings.STORAGES)
    storages["staticfiles"] = {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }
    settings.STORAGES = storages

    # WhiteNoise middleware warns when STATIC_ROOT does not exist.
    Path(settings.STATIC_ROOT).mkdir(parents=True, exist_ok=True)


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
