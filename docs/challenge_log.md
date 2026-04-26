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

## CH-005 — (placeholder for next challenge)

*To be completed when the next challenge arises.*

---
