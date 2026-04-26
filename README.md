# MDN LocalLibrary — Multi-Level Automated Testing Project

> **Attribution:** Application under test is the [Django Local Library tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Tutorial_local_library_website) by [MDN Web Docs contributors](https://developer.mozilla.org/en-US/docs/MDN/Community/Contributing), licensed [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/). Upstream repo: [mdn/django-locallibrary-tutorial](https://github.com/mdn/django-locallibrary-tutorial). Original application code belongs to its respective authors; this fork layers a structured automated-testing programme on top.

---

## Overview

A software quality assurance study project built on MDN's Django tutorial app — a modest library catalogue that, frankly, turns out to be a pretty ideal specimen for demonstrating a full test-pyramid implementation. On top of the original Django application, this repo adds a DRF REST API, borrow/return workflows, and nine test phases ranging from isolated unit assertions up to Selenium end-to-end journeys.

Test strategy lives in [docs/master_test_plan.md](docs/master_test_plan.md). Every stumble along the way is catalogued in [docs/challenge_log.md](docs/challenge_log.md).

---

## Phase 1 evidence

Baseline setup evidence is organised by phase under [docs/evidence/](docs/evidence/).

- [docs/evidence/README.md](docs/evidence/README.md) — evidence index for all project phases
- [docs/evidence/phase-1/README.md](docs/evidence/phase-1/README.md) — Phase 1 proof page with embedded screenshots and verification notes

These artefacts support the completed baseline verification and should be extended phase by phase as new evidence is generated.

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
├── locallibrary/         # Project settings, root URL conf, WSGI/ASGI
├── templates/            # Project-level auth/registration templates
├── docs/                 # Test plan, challenge log, evidence, traceability matrix, defect log
├── requirements.txt      # Local dev dependencies (SQLite, no psycopg2)
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
uv pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

| URL | Page |
|-----|------|
| `http://127.0.0.1:8000/catalog/` | Catalogue home |
| `http://127.0.0.1:8000/accounts/login/` | Member login |
| `http://127.0.0.1:8000/admin/` | Django admin |

---

## Running tests

Upstream suite (models, forms, views — basic coverage):

```bash
python manage.py test
```

Extended pytest suite (once Phases 4–8 are complete):

```bash
pytest                               # all non-system tests
RUN_SYSTEM_TESTS=1 pytest -m system  # Selenium journeys
```

---

## Testing phases

| # | Scope | Status |
|---|-------|--------|
| 1 | Baseline setup and environment | Complete |
| 2 | DRF REST API | Planned |
| 3 | Borrow/return/search workflows | Planned |
| 4 | Unit tests + coverage | Planned |
| 5 | Django client integration tests | Planned |
| 6 | Requests-based API integration tests | Planned |
| 7 | Selenium system tests | Planned |
| 8 | Consolidated coverage push | Planned |
| 9 | Final documentation and reporting | Planned |

---

## Licence

**Application code** (`catalog/`, `locallibrary/`) — [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/) (MDN).

**Tests, documentation, and project configuration** — [MIT](LICENSE).
