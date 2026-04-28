"""Compact integration tests for catalog general views and delete branches."""

import uuid

import pytest
from django.test import Client
from django.urls import reverse

from catalog.models import Author, Book
from tests.fixtures.sample_data import DEFAULT_BOOK_SUMMARY

pytestmark = [pytest.mark.integration_client, pytest.mark.django_db]


def _unique_13_digit_number():
    return f"{uuid.uuid4().int % (10 ** 13):013d}"


def _create_book(title, author, language, genre):
    book = Book.objects.create(
        title=title,
        summary=DEFAULT_BOOK_SUMMARY,
        isbn=_unique_13_digit_number(),
        author=author,
        language=language,
    )
    book.genre.add(genre)
    return book


def test_index_displays_counts_and_increments_visit_counter(
    catalog_book, available_book_instance
):
    """Cover index metrics context and session-based visit counting."""
    assert available_book_instance.book_id == catalog_book.pk
    client = Client()

    first_response = client.get(reverse("index"))
    assert first_response.status_code == 200
    assert first_response.context["num_books"] >= 1
    assert first_response.context["num_instances"] >= 1
    assert first_response.context["num_instances_available"] >= 1
    assert first_response.context["num_authors"] >= 1
    assert first_response.context["num_visits"] == 1

    second_response = client.get(reverse("index"))
    assert second_response.status_code == 200
    assert second_response.context["num_visits"] == 2


def test_public_catalog_views_return_success(
    catalog_book, catalog_author, catalog_language, available_book_instance
):
    """Public list/detail routes should respond successfully for valid fixtures."""
    genre = catalog_book.genre.first()
    assert genre is not None
    urls = [
        reverse("books"),
        reverse("book-detail", args=[catalog_book.pk]),
        reverse("authors"),
        reverse("author-detail", args=[catalog_author.pk]),
        reverse("genres"),
        reverse("genre-detail", args=[genre.pk]),
        reverse("languages"),
        reverse("language-detail", args=[catalog_language.pk]),
        reverse("bookinstances"),
        reverse("bookinstance-detail", args=[available_book_instance.pk]),
    ]

    client = Client()
    for url in urls:
        response = client.get(url)
        assert response.status_code == 200


def test_author_delete_with_related_books_redirects_back_to_delete(
    catalog_author, catalog_book, editor_user
):
    """Author delete exception path keeps record and redirects back to delete page."""
    assert catalog_book.author_id == catalog_author.pk
    client = Client()
    client.force_login(editor_user)

    response = client.post(reverse("author-delete", args=[catalog_author.pk]))
    assert response.status_code == 302
    assert reverse("author-delete", args=[catalog_author.pk]) in response["Location"]
    assert Author.objects.filter(pk=catalog_author.pk).exists()


def test_author_delete_without_related_books_redirects_to_list(editor_user):
    """Author delete success path removes record and redirects to authors list."""
    author = Author.objects.create(first_name="Delete", last_name="Me")
    client = Client()
    client.force_login(editor_user)

    response = client.post(reverse("author-delete", args=[author.pk]))
    assert response.status_code == 302
    assert reverse("authors") in response["Location"]
    assert not Author.objects.filter(pk=author.pk).exists()


def test_book_delete_with_related_instances_redirects_back_to_delete(
    catalog_book, available_book_instance, editor_user
):
    """Book delete exception path keeps record and redirects back to delete page."""
    assert available_book_instance.book_id == catalog_book.pk
    client = Client()
    client.force_login(editor_user)

    response = client.post(reverse("book-delete", args=[catalog_book.pk]))
    assert response.status_code == 302
    assert reverse("book-delete", args=[catalog_book.pk]) in response["Location"]
    assert Book.objects.filter(pk=catalog_book.pk).exists()


def test_book_delete_without_instances_redirects_to_list(
    catalog_author, catalog_language, catalog_book, editor_user
):
    """Book delete success path removes record and redirects to books list."""
    standalone_book = _create_book(
        title="A Temporary Standalone Book",
        author=catalog_author,
        language=catalog_language,
        genre=catalog_book.genre.first(),
    )

    client = Client()
    client.force_login(editor_user)

    response = client.post(reverse("book-delete", args=[standalone_book.pk]))
    assert response.status_code == 302
    assert reverse("books") in response["Location"]
    assert not Book.objects.filter(pk=standalone_book.pk).exists()
