import datetime

import pytest
from django.urls import reverse

from catalog.models import Author, Book, BookInstance, Genre, Language


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


def test_genre_string_and_absolute_url():
    genre = Genre.objects.create(name="Mystery")

    assert str(genre) == "Mystery"
    assert genre.get_absolute_url() == reverse("genre-detail", args=[genre.id])


def test_language_string_and_absolute_url():
    language = Language.objects.create(name="French")

    assert str(language) == "French"
    assert language.get_absolute_url() == reverse("language-detail", args=[language.id])


def test_book_string_and_absolute_url(catalog_book):
    assert str(catalog_book) == "Frankenstein"
    assert catalog_book.get_absolute_url() == reverse(
        "book-detail", args=[catalog_book.id]
    )


def test_book_display_genre_limits_output_to_first_three(
    catalog_author, catalog_language
):
    book = Book.objects.create(
        title="Genre Sampler",
        summary="Book used to validate display_genre behavior.",
        isbn="1111111111111",
        author=catalog_author,
        language=catalog_language,
    )
    genre_names = ["Adventure", "Mystery", "Sci-Fi", "Drama"]
    genres = [Genre.objects.create(name=name) for name in genre_names]
    book.genre.add(*genres)

    assert book.display_genre() == "Adventure, Mystery, Sci-Fi"


def test_book_instance_is_overdue_true_for_past_date(catalog_book):
    instance = BookInstance.objects.create(
        book=catalog_book,
        imprint="Test imprint",
        due_back=datetime.date.today() - datetime.timedelta(days=1),
        status="o",
    )

    assert instance.is_overdue is True


def test_book_instance_is_overdue_false_for_today_and_none(catalog_book):
    due_today_instance = BookInstance.objects.create(
        book=catalog_book,
        imprint="Due today",
        due_back=datetime.date.today(),
        status="o",
    )
    no_due_date_instance = BookInstance.objects.create(
        book=catalog_book,
        imprint="No due date",
        due_back=None,
        status="a",
    )

    assert due_today_instance.is_overdue is False
    assert no_due_date_instance.is_overdue is False


def test_book_instance_string_and_absolute_url(catalog_book):
    instance = BookInstance.objects.create(
        book=catalog_book,
        imprint="Instance string test",
        status="a",
    )

    assert str(instance) == f"{instance.id} (Frankenstein)"
    assert instance.get_absolute_url() == reverse(
        "bookinstance-detail", args=[instance.id]
    )


def test_book_instance_string_falls_back_when_book_missing():
    instance = BookInstance.objects.create(
        book=None,
        imprint="Fallback string test",
        status="d",
    )

    assert str(instance).endswith("(Unknown book)")


def test_author_string_and_absolute_url():
    author = Author.objects.create(first_name="Jane", last_name="Austen")

    assert str(author) == "Austen, Jane"
    assert author.get_absolute_url() == reverse("author-detail", args=[author.id])
