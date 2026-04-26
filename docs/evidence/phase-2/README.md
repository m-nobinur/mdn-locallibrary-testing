# Phase 2 Evidence — DRF REST API Integration

This folder contains the verification evidence for Phase 2 of the project, covering the Django REST Framework API layer added on top of the MDN LocalLibrary application.

## What this phase proves

- `djangorestframework==3.15.2` installed cleanly from `requirements-dev.txt`
- `rest_framework` and `rest_framework.authtoken` added to `INSTALLED_APPS`
- `authtoken` migrations applied without errors
- All four API URL names resolve to their expected paths
- Django system check reports zero issues with the new configuration
- Read-only endpoints exist for books, authors, and book instances
- Token authentication endpoint is exposed at `/api/auth/token/`

## New files added

| File | Purpose |
|------|---------|
| `requirements-dev.txt` | DRF and test tooling dependencies, separate from the runtime |
| `catalog/api/__init__.py` | Package marker |
| `catalog/api/serializers.py` | Read-only serializers for `Book`, `Author`, `BookInstance`, `Genre`, `Language` |
| `catalog/api/views.py` | `ReadOnlyModelViewSet` classes for each resource |
| `catalog/api/urls.py` | `DefaultRouter` registering all three viewsets |

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
print('Token URL:', reverse('api-token-auth'))
print('Books URL:', reverse('book-list'))
print('Authors URL:', reverse('author-list'))
print('BookInstances URL:', reverse('bookinstance-list'))
"
Token URL:         /api/auth/token/
Books URL:         /api/books/
Authors URL:       /api/authors/
BookInstances URL: /api/book-instances/
```
