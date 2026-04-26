from django.urls import path, include
from rest_framework.routers import DefaultRouter

from catalog.api.views import AuthorViewSet, BookViewSet, BookInstanceViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'book-instances', BookInstanceViewSet, basename='bookinstance')

urlpatterns = [
    path('', include(router.urls)),
]
