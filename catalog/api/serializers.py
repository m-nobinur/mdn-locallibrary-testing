from rest_framework import serializers

from catalog.models import Author, Book, BookInstance, Genre, Language


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'date_of_death']


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'summary', 'isbn', 'genre', 'language']


class BookInstanceSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    borrower = serializers.StringRelatedField()

    class Meta:
        model = BookInstance
        fields = ['id', 'book', 'imprint', 'due_back', 'status', 'borrower', 'is_overdue']
