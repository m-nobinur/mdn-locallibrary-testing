# Challenge Log — MDN LocalLibrary Automated Testing Project

This log records every significant obstacle, version conflict, or unexpected behaviour encountered during the project — along with what was tried, what eventually worked, and what anyone picking up this repo should know before they waste an afternoon on the same thing.

---

## CH-001 — psycopg2-binary fails to build on Python 3.14

- **Date:** 2026-04-26
- **Phase:** Phase 1
- **Severity:** High

### Symptom

Running `uv pip install -r requirements.txt` failed with a `clang` compilation error deep inside `psycopg2-binary==2.9.9`:

```text
psycopg/utils.c:397:12: error: call to undeclared function '_PyInterpreterState_Get';
ISO C99 and later do not support implicit function declarations
```

The build aborted entirely, leaving no packages installed.

### Root cause

`psycopg2-binary 2.9.9` uses the internal CPython C API function `_PyInterpreterState_Get` (note the leading underscore). That private symbol was removed in CPython 3.14 as part of ongoing internal API stabilisation work. The package's C extension code also calls `PyWeakref_GetObject`, which was deprecated in Python 3.13 and is now marked with `__attribute__((__deprecated__))`, generating warnings — though warnings alone didn't block the build. The fatal error was the undeclared `_PyInterpreterState_Get`.

At the time of writing (April 2026), `psycopg2` has not yet cut a release that supports Python 3.14. The 2.9.x series is effectively frozen for older Python versions. `psycopg3` (the `psycopg` package, not `psycopg2`) does support Python 3.14, but it's a different API.

### Investigation

1. Ran `uv pip install -r requirements.txt` — build failed as above.
2. Confirmed the Python version: `.venv/bin/python --version` → `Python 3.14.4`.
3. Checked `runtime.txt` — it says `python-3.10.2`, which is what Heroku would use. The local `.venv` was created against the system Python, not the pinned version.
4. Searched PyPI for `psycopg2-binary` wheel availability for `cp314` — no wheels exist for Python 3.14 at this point.
5. Checked whether the project actually uses PostgreSQL locally — `locallibrary/settings.py` defaults to SQLite; `psycopg2` is only needed when `DATABASE_URL` is set in the environment.

### Resolution

Removed `psycopg2-binary==2.9.9` from `requirements.txt` and documented it there with a comment. Created a separate `requirements-prod.txt` (which `pip install`s `requirements.txt` first, then adds `psycopg2-binary`) to keep the production dependency available for anyone deploying to Heroku or Railway on Python ≤ 3.13.

`uv pip install -r requirements.txt` then completed successfully, installing 10 packages.

### Impact

Without this fix, nobody running Python 3.14 could install the project's dependencies at all — let alone run the app or write tests. The separation into `requirements.txt` / `requirements-prod.txt` also clarifies the boundary between what's needed to run the app locally and what's needed for a PostgreSQL-backed production deployment.

---

## CH-002 — Phase 2 completed without blocking challenges

- **Date:** 2026-04-26
- **Phase:** Phase 2
- **Severity:** N/A

### Summary

Phase 2 DRF integration completed cleanly. No blocking issues were encountered during dependency installation, settings configuration, serializer/viewset implementation, migration, or URL resolution verification.

---

## CH-003 — Pylint E1101 false positives on Django ORM field descriptors

- **Date:** 2026-04-27
- **Phase:** Phase 2
- **Severity:** Low

### Symptom

Pylint reported `E1101:no-member` on two lines in `catalog/models.py`:

```md
Instance of 'ForeignKey' has no 'title' member       (BookInstance.__str__)
Instance of 'ManyToManyField' has no 'all' member    (Book.display_genre)
```

### Root cause

Pylint analyses Django model field descriptors statically. At definition time `book` is a `ForeignKey` instance and `genre` is a `ManyToManyField` instance — neither carries the resolved related-model attributes that only exist at runtime after Django's model metaclass wiring runs. Without `django-stubs`, Pylint has no way to know that `self.book` resolves to a `Book` instance at runtime.

### Resolution

- `BookInstance.__str__`: replaced direct `self.book.title` access with `str(self.book)` via a safe label variable (`book_label = self.book if self.book else 'Unknown book'`), which avoids the attribute access entirely and also handles the `null=True` case correctly.
- `Book.display_genre`: replaced `self.genre.all()[:3]` with `Genre.objects.filter(book=self).values_list('name', flat=True)[:3]`, querying via the model manager instead of the descriptor.
- `Genre.__str__`: wrapped `return self.name` in `str()` to satisfy the strict return-type checker.

---

## CH-004 — Preventing unsafe state changes in borrow/return workflows

- **Date:** 2026-04-27
- **Phase:** Phase 3
- **Severity:** Medium

### Symptom

The new borrow and return actions could have been implemented as plain links (`GET`) from list/detail pages, which makes testing simple but allows state changes via refreshes, crawlers, or copied URLs.

### Root cause

Initial template patterns in the tutorial code mostly use links, and there was no existing borrow/return workflow to enforce a safer mutation pattern.

### Investigation

1. Compared renewal flow and existing list templates.
2. Reviewed where borrow/return controls would appear (book detail, borrowed list, all copies list).
3. Evaluated URL and permission implications for member vs librarian actions.

### Resolution

- Added `catalog/services.py` so state transitions live in one place.
- Implemented borrow/return as `POST` actions with CSRF protection.
- Added safe `next` redirect handling so workflow pages can return users to the correct location without open redirects.
- Added flash-message feedback in the base template so result of each action is explicit.

### Impact

Without this, the workflow would be vulnerable to accidental or unsafe mutations and harder to reason about in later integration and system tests.

---

## CH-005 — Pytest emits Django deprecation warnings on Python 3.14

- **Date:** 2026-04-27
- **Phase:** Phase 4
- **Severity:** Low

### Symptom

Unit tests passed, but pytest printed repeated `DeprecationWarning` entries from Django auth decorators:

```text
DeprecationWarning: 'asyncio.iscoroutinefunction' is deprecated and slated for removal in Python 3.16
```

### Root cause

This warning originates in Django internals on the current local interpreter (`Python 3.14.4`), not in project test logic. Django currently calls `asyncio.iscoroutinefunction`, which now warns in Python 3.14 and is planned for removal in Python 3.16.

### Investigation

1. Verified warning stack traces point to `django/contrib/auth/decorators.py` inside `.venv`.
2. Re-ran unit tests and confirmed no failing assertions or local code references to `asyncio.iscoroutinefunction`.
3. Confirmed warning appears consistently on Python 3.14 while test outcomes remain stable.

### Resolution

- Logged the warning as a known environment-level issue.
- Captured it in `docs/defect_log.csv` as `DEF-P4-001`.
- Kept tests and fixtures unchanged because application behavior is correct.

### Impact

No functional impact on Phase 4 deliverables. Risk is future-facing: warning noise can hide real failures if ignored and may become a hard incompatibility if interpreter versions advance ahead of framework updates.

---

## CH-006 — DRF route names collided with catalog HTML route names

- **Date:** 2026-04-27
- **Phase:** Phase 4
- **Severity:** Medium

### Symptom

`catalog/tests/test_models.py::AuthorModelTest::test_get_absolute_url` failed because `Author.get_absolute_url()` returned an API URL:

```text
'/api/authors/1/' != '/catalog/author/1'
```

This also cascaded into `AuthorCreate` redirect assertions in `catalog/tests/test_views.py`.

### Root cause

The DRF router in `catalog/api/urls.py` created names like `author-detail`, `book-detail`, and `genre-detail`. Because `locallibrary/urls.py` included those API routes without a namespace, they shared global route names with the HTML views in `catalog/urls.py`. As a result, `reverse("author-detail")` in `catalog/models.py` could resolve to the API endpoint instead of the catalog page.

### Investigation

1. Reproduced failures with `pytest catalog/tests -q`.
2. Confirmed `Author.get_absolute_url()` still uses `reverse("author-detail")`.
3. Checked URL configuration and found un-namespaced `path('api/', include('catalog.api.urls'))`.
4. Verified DRF `DefaultRouter` generated conflicting names.

### Resolution

- Added `app_name = 'catalog_api'` in `catalog/api/urls.py`.
- Updated `locallibrary/urls.py` to include API routes under the explicit namespace `catalog_api`.
- Re-ran the catalog suite to verify model URL assertions now resolve to catalog HTML routes.

### Impact

Restored deterministic URL reversing for model `get_absolute_url()` methods and removed API-vs-HTML route ambiguity.

---

## CH-007 — Django test client context copy crash on Python 3.14

- **Date:** 2026-04-27
- **Phase:** Phase 4
- **Severity:** High

### Symptom

Multiple catalog view tests crashed during template rendering with:

```text
AttributeError: 'super' object has no attribute 'dicts'
```

The traceback consistently pointed to Django internals: `django/template/context.py` via `django/test/client.py::store_rendered_templates`.

### Root cause

On the local toolchain (`Python 3.14.4`), Django's context copy path used by test instrumentation (`copy(context)`) fails for `RequestContext`/`BaseContext` objects. This is an environment/framework compatibility issue, not an application view bug.

### Investigation

1. Confirmed stack traces terminate in Django internals before test assertions run.
2. Reviewed `django/test/client.py` and identified `store_rendered_templates()` as the failure point.
3. Verified failures occurred across unrelated template-rendering tests.

### Resolution

- Added a Python 3.14 compatibility shim in `conftest.py` inside `pytest_configure()`.
- Patched `django.test.client.store_rendered_templates` to:
	- keep Django's normal behavior when `copy(context)` succeeds,
	- fall back to a flattened context snapshot when that copy raises `AttributeError`.

### Impact

Re-enabled template-rendering assertions (`response.context`, `assertTemplateUsed`, redirect follow checks) across the catalog test suite on Python 3.14.

---

## CH-008 — WhiteNoise manifest static storage blocked template rendering in tests

- **Date:** 2026-04-27
- **Phase:** Phase 4
- **Severity:** Medium

### Symptom

After fixing context-copy crashes, view tests failed with:

```text
ValueError: Missing staticfiles manifest entry for 'css/styles.css'
```

### Root cause

`locallibrary/settings.py` uses `whitenoise.storage.CompressedManifestStaticFilesStorage` via `STORAGES['staticfiles']`. In local test runs without a prebuilt `collectstatic` manifest, template `{% static %}` resolution fails.

### Investigation

1. Re-ran `pytest catalog/tests -q` after the context-copy fix.
2. Confirmed failures moved to static template tag resolution in WhiteNoise storage.
3. Verified no staticfiles manifest had been generated in test context.

### Resolution

- Added an autouse pytest fixture in `conftest.py` to set test-time staticfiles backend to:
	- `django.contrib.staticfiles.storage.StaticFilesStorage`

This keeps production static handling unchanged while making unit tests independent of manifest build artifacts.

### Impact

Catalog view tests now render templates reliably in local CI-style runs without requiring `collectstatic` as a pre-step.

---

## CH-009 — Warning noise in pytest output after functional fixes

- **Date:** 2026-04-28
- **Phase:** Phase 4
- **Severity:** Low

### Symptom

After catalog tests were passing, pytest still emitted warning noise from two sources:

```text
DeprecationWarning: 'asyncio.iscoroutinefunction' is deprecated ...
UserWarning: No directory at: .../staticfiles/
```

### Root cause

- The deprecation warnings are produced by Django internals (`django.contrib.auth.decorators`) on Python 3.14.
- The staticfiles warning is raised by WhiteNoise middleware when `STATIC_ROOT` does not exist at test startup.

### Investigation

1. Re-ran `pytest catalog/tests -q` after functional repairs.
2. Verified warning sources in stack traces and confirmed warnings came from framework/runtime setup rather than application logic.
3. Confirmed warning volume obscured normal test output.

### Resolution

- Added targeted `filterwarnings` in `pytest.ini` for the known Django/Python 3.14 deprecation pattern.
- Updated `conftest.py` test fixture to create `STATIC_ROOT` automatically (`Path(settings.STATIC_ROOT).mkdir(...)`) during pytest runs.

### Impact

Catalog test output is significantly cleaner, while warning handling remains explicit and constrained to test execution.

---
