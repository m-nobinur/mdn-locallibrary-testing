# Phase 2 Evidence — DRF REST API Integration

This folder contains the verification evidence for Phase 2 of the project, covering the Django REST Framework API layer added on top of the MDN LocalLibrary application.

## What this phase proves

- `djangorestframework==3.15.2` installed cleanly from `requirements-dev.txt`
- `rest_framework` and `rest_framework.authtoken` added to `INSTALLED_APPS`
- `authtoken` migrations applied without errors
- All API URL names resolve to their expected paths (see verification output below)
- Django system check reports zero issues with the full API configuration
- Read-only endpoints exist for books, authors, book instances, genres, and languages
- Token authentication endpoint is exposed at `/api/auth/token/`
- All list endpoints support `?search=` and `?ordering=` querystring parameters
- Book instance list additionally supports `?status=a|o|d|r` availability filter
- Catalogue statistics endpoint exposed at `/api/stats/`
- URL registration bug corrected: `locallibrary/urls.py` now correctly includes both `catalog.api.urls` and `api/auth/token/`

## New files added

| File | Purpose |
|------|---------|
| `requirements-dev.txt` | DRF and test tooling dependencies, separate from the runtime |
| `catalog/api/__init__.py` | Package marker |
| `catalog/api/serializers.py` | Read-only serializers for `Book`, `Author`, `BookInstance`, `Genre`, `Language` |
| `catalog/api/views.py` | `ReadOnlyModelViewSet` for all five resources; `SearchFilter` and `OrderingFilter` on all viewsets; `?status=` param on `BookInstanceViewSet`; `catalog_stats` function view |
| `catalog/api/urls.py` | `DefaultRouter` registering all five viewsets plus `/stats/` route |

## Settings changes

`locallibrary/settings.py` — additions:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

`locallibrary/urls.py` — additions:

```python
path('api/', include('catalog.api.urls')),
path('api/auth/token/', obtain_auth_token, name='api-token-auth'),
```

## API surface

| Endpoint | Method | Querystring support |
|----------|--------|---------------------|
| `/api/books/` | GET | `?search=`, `?ordering=` |
| `/api/books/<id>/` | GET | — |
| `/api/authors/` | GET | `?search=`, `?ordering=` |
| `/api/authors/<id>/` | GET | — |
| `/api/book-instances/` | GET | `?search=`, `?status=a\|o\|d\|r`, `?ordering=` |
| `/api/book-instances/<id>/` | GET | — |
| `/api/genres/` | GET | `?search=` |
| `/api/genres/<id>/` | GET | — |
| `/api/languages/` | GET | `?search=` |
| `/api/languages/<id>/` | GET | — |
| `/api/stats/` | GET | — |
| `/api/auth/token/` | POST | — |

## Verification steps run

### 1. System check

```bash
$ python manage.py check
System check identified no issues (0 silenced).
```

### 2. URL resolution

```bash
$ python manage.py shell -c "
from django.urls import reverse
print('Token URL:          ', reverse('api-token-auth'))
print('Books URL:          ', reverse('book-list'))
print('Authors URL:        ', reverse('author-list'))
print('BookInstances URL:  ', reverse('bookinstance-list'))
print('Genres URL:         ', reverse('genre-list'))
print('Languages URL:      ', reverse('language-list'))
print('Stats URL:          ', reverse('api-stats'))
"
Token URL:           /api/auth/token/
Books URL:           /api/books/
Authors URL:         /api/authors/
BookInstances URL:   /api/book-instances/
Genres URL:          /api/genres/
Languages URL:       /api/languages/
Stats URL:           /api/stats/
```
