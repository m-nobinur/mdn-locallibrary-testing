from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from catalog.models import Author, Book, BookInstance, Genre, Language
from catalog.api.serializers import (
    AuthorSerializer,
    BookSerializer,
    BookInstanceSerializer,
    GenreSerializer,
    LanguageSerializer,
)


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.select_related('author', 'language').prefetch_related('genre').order_by('title')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'author__first_name', 'author__last_name', 'isbn']
    ordering_fields = ['title', 'author__last_name']


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all().order_by('last_name', 'first_name')
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['last_name', 'first_name']


class BookInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookInstance.objects.select_related('book', 'borrower').order_by('due_back')
    serializer_class = BookInstanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['book__title', 'borrower__username']
    ordering_fields = ['due_back', 'status']

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Language.objects.all().order_by('name')
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']


@api_view(['GET'])
def catalog_stats(request):
    """Return summary statistics for the library catalogue."""
    data = {
        'total_books': Book.objects.count(),
        'total_book_instances': BookInstance.objects.count(),
        'available_book_instances': BookInstance.objects.filter(status='a').count(),
        'on_loan_book_instances': BookInstance.objects.filter(status='o').count(),
        'total_authors': Author.objects.count(),
        'total_genres': Genre.objects.count(),
        'total_languages': Language.objects.count(),
    }
    return Response(data)
