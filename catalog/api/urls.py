from django.urls import path, include
from rest_framework.routers import DefaultRouter

from catalog.api.views import (
    AuthorViewSet,
    BookViewSet,
    BookInstanceViewSet,
    GenreViewSet,
    LanguageViewSet,
    catalog_stats,
)

app_name = 'catalog_api'

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'book-instances', BookInstanceViewSet, basename='bookinstance')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'languages', LanguageViewSet, basename='language')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', catalog_stats, name='api-stats'),
]
