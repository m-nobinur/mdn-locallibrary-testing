# MDN LocalLibrary — Multi-Level Automated Testing Project

> **Attribution:** Application under test is the [Django Local Library tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Tutorial_local_library_website) by [MDN Web Docs contributors](https://developer.mozilla.org/en-US/docs/MDN/Community/Contributing), licensed [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/). Upstream repo: [mdn/django-locallibrary-tutorial](https://github.com/mdn/django-locallibrary-tutorial). Original application code belongs to its respective authors; this fork layers a structured automated-testing programme on top.

---

## Overview

A software quality assurance study project built on MDN's Django tutorial app — a modest library catalogue that, frankly, turns out to be a pretty ideal specimen for demonstrating a full test-pyramid implementation. On top of the original Django application, this repo adds a DRF REST API, borrow/return workflows, and nine test phases ranging from isolated unit assertions up to Selenium end-to-end journeys.

Test strategy lives in [docs/master_test_plan.md](docs/master_test_plan.md). Every stumble along the way is catalogued in [docs/challenge_log.md](docs/challenge_log.md).

---

## Phase evidence

Evidence artefacts are organised by delivery phase under [docs/evidence/](docs/evidence/).

| Phase | Evidence |
| --- | --- |
| 1 — Baseline setup | [docs/evidence/phase-1/README.md](docs/evidence/phase-1/README.md) — home page, admin dashboard, GitHub repo screenshots |
| 2 — DRF API | [docs/evidence/phase-2/README.md](docs/evidence/phase-2/README.md) — migration output, URL resolution, system check verification |
| 3 — Search/borrow/return workflows | [docs/evidence/phase-3/README.md](docs/evidence/phase-3/README.md) — manual verification screenshots |
| 4 — Unit testing and coverage | [docs/evidence/phase-4/README.md](docs/evidence/phase-4/README.md) — pytest unit report, HTML coverage report, manual screenshot evidence |
| 5 — Django client integration tests | [docs/evidence/phase-5/README.md](docs/evidence/phase-5/README.md) — streamlined 30-test suite, catalog/views.py 100% coverage, HTML test report and coverage screenshots |
| 6 — Requests-based API integration tests | [docs/evidence/phase-6/README.md](docs/evidence/phase-6/README.md) — 18 HTTP API integration tests across token/books/authors/book-instances/genres/languages/stats with 100% `catalog.api` coverage |

---

## The application

LocalLibrary models a small public lending library. Unauthenticated visitors browse books and authors; authenticated members manage loan renewals; librarian-role users get full administrative control.

Core entities: **Book**, **BookInstance** (individual copy, carries loan status and due-back date), **Author**, **Genre**, **Language**.

![Data model UML](https://raw.githubusercontent.com/mdn/django-locallibrary-tutorial/master/catalog/static/images/local_library_model_uml.png)

---

## Repository layout

```md
mdn-locallibrary-testing/
├── catalog/              # Django app — models, views, forms, URLs, templates
│   └── api/              # DRF serializers, viewsets, and router (Phase 2)
├── locallibrary/         # Project settings, root URL conf, WSGI/ASGI
├── templates/            # Project-level auth/registration templates
├── docs/                 # Test plan, challenge log, evidence, traceability matrix, defect log
├── requirements.txt      # Runtime dependencies (SQLite-only, no psycopg2)
├── requirements-dev.txt  # DRF and testing dependencies (pytest, coverage, requests)
├── requirements-prod.txt # Adds psycopg2 for PostgreSQL deployments on Python ≤ 3.13
├── manage.py
└── runtime.txt           # Python version pin for production deployments
```

---

## Compatibility notes

**Python 3.14 and psycopg2.** Python 3.14 may still be usable for local SQLite-only experimentation, but it is outside Django 5.1.x's officially supported matrix and breaks `psycopg2-binary==2.9.9` because the C extension references `_PyInterpreterState_Get`, a private CPython symbol removed in 3.14. Since the default local setup uses SQLite, the PostgreSQL driver is not required there. For PostgreSQL-backed deployments matching production, use [requirements-prod.txt](requirements-prod.txt). Full details in [docs/challenge_log.md](docs/challenge_log.md) (CH-001).

`runtime.txt` currently pins production deployments to **Python 3.10.2**. To keep local development, CI, and production aligned, prefer Python 3.10 for day-to-day work unless you are intentionally testing a different interpreter.

Django 5.1.x officially supports Python 3.10–3.13. If you prefer a pinned-stable environment that matches production, `uv venv .venv --python 3.10` is the safest option.

---

## Quick start

Requires [uv](https://github.com/astral-sh/uv). Plain `pip` works too — substitute as needed.

```bash
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt          # runtime
uv pip install -r requirements-dev.txt      # DRF + test tools
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

| URL | Page |
| ----- | ------ |
| `http://127.0.0.1:8000/catalog/` | Catalogue home |
| `http://127.0.0.1:8000/accounts/login/` | Member login |
| `http://127.0.0.1:8000/admin/` | Django admin |
| `http://127.0.0.1:8000/api/` | DRF browsable API root |
| `http://127.0.0.1:8000/api/books/` | Book list (token required) |
| `http://127.0.0.1:8000/api/authors/` | Author list (token required) |
| `http://127.0.0.1:8000/api/book-instances/` | Book instance list (token required) |
| `http://127.0.0.1:8000/api/genres/` | Genre list (token required) |
| `http://127.0.0.1:8000/api/languages/` | Language list (token required) |
| `http://127.0.0.1:8000/api/stats/` | Catalogue statistics summary (token required) |
| `http://127.0.0.1:8000/api/auth/token/` | Obtain auth token (POST) |

All list endpoints support `?search=<term>` and `?ordering=<field>`. Book instances additionally support `?status=a|o|d|r` to filter by availability.

### Obtaining an API token

```bash
curl -s -X POST http://127.0.0.1:8000/api/auth/token/ \
  -d "username=<user>&password=<pass>" | python -m json.tool
# {"token": "<your-token>"}

# List all books
curl -s http://127.0.0.1:8000/api/books/ \
  -H "Authorization: Token <your-token>" | python -m json.tool

# Search books by title or author
curl -s "http://127.0.0.1:8000/api/books/?search=tolkien" \
  -H "Authorization: Token <your-token>" | python -m json.tool

# Filter book instances by availability status
curl -s "http://127.0.0.1:8000/api/book-instances/?status=a" \
  -H "Authorization: Token <your-token>" | python -m json.tool

# Get catalogue-wide statistics
curl -s http://127.0.0.1:8000/api/stats/ \
  -H "Authorization: Token <your-token>" | python -m json.tool
```

---

## Running tests

Upstream suite (models, forms, views — basic coverage):

```bash
python manage.py test
```

Extended pytest suite (once Phases 4–8 are complete):

```bash
pytest -m unit --cov=catalog.forms --cov=catalog.models --cov=catalog.services \
  --cov-report=term-missing --cov-report=html:reports/coverage-html \
  --html=reports/unit-report.html --self-contained-html
pytest                                 # all non-system tests
RUN_SYSTEM_TESTS=1 pytest -m system    # Selenium journeys
```

### Test compatibility hooks

This repository includes a few test-only compatibility hooks for local Python 3.14 runs:

- A safe fallback patch for Django's test-client template context copying (avoids the known `RequestContext` copy crash).
- A test-time staticfiles backend override (`StaticFilesStorage`) so tests do not depend on a prebuilt WhiteNoise manifest.
- Automatic creation of `STATIC_ROOT` during tests to avoid middleware warnings about a missing staticfiles directory.

`pytest` applies these via `conftest.py`; `python manage.py test` applies equivalent test-only compatibility from settings when the `test` command is used. They do not change production runtime behaviour.

---

## Linting and import sorting

Run checks with the repository configuration files (`.pylintrc` and `.isort.cfg`):

```bash
python -m isort --check-only .
python -m pylint catalog locallibrary manage.py
```

Auto-fix import ordering:

```bash
python -m isort .
```

---

## Testing phases

| #   | Scope                                | Status   |
| --- | ------------------------------------ | -------- |
| 1   | Baseline setup and environment       | Complete |
| 2   | DRF REST API                         | Complete |
| 3   | Borrow/return/search workflows       | Complete |
| 4   | Unit tests + coverage                | Complete |
| 5   | Django client integration tests      | Complete |
| 6   | Requests-based API integration tests | Complete |
| 7   | Selenium system tests                | Planned  |
| 8   | Consolidated coverage push           | Planned  |
| 9   | Final documentation and reporting    | Planned  |

---

## Licence

**Application code** (`catalog/`, `locallibrary/`) — [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/) (MDN).

**Tests, documentation, and project configuration** — [MIT](LICENSE).
