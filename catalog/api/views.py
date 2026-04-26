from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from catalog.models import Author, Book, BookInstance
from catalog.api.serializers import AuthorSerializer, BookSerializer, BookInstanceSerializer


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.select_related('author', 'language').prefetch_related('genre').order_by('title')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all().order_by('last_name', 'first_name')
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]


class BookInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookInstance.objects.select_related('book', 'borrower').order_by('due_back')
    serializer_class = BookInstanceSerializer
    permission_classes = [IsAuthenticated]
