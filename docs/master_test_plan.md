# Master Test Plan — MDN LocalLibrary Automated Testing Project

**Document version:** 1.8  
**Last updated:** 2026-04-29  
**Project phase:** Phase 7 — Browser E2E UI Tests  
**Author:** Project contributor  
**Application under test:** Django LocalLibrary (MDN tutorial fork)

---

## 1. Introduction and scope

This document is the living master test plan for the MDN LocalLibrary automated testing project. It covers what's being tested, why, how, and to what standard — from unit-level assertions through to full end-to-end browser journeys.

The application under test is a Django-based library catalogue originally authored by [MDN Web Docs contributors](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Tutorial_local_library_website). The upstream source is at [mdn/django-locallibrary-tutorial](https://github.com/mdn/django-locallibrary-tutorial) and is licensed under CC BY-SA 2.5. This fork layers a structured, multi-level testing strategy on top of the application — it adds features specifically to make interesting things worth testing (a REST API, borrow/return workflows) and then tests all of it thoroughly.

### 1.1 What is in scope

- All Django application code in `catalog/` and `locallibrary/`
- The Django REST Framework API endpoints added in Phase 2
- The borrow, return, and search workflows added in Phase 3
- User authentication and role-based access control
- Data model integrity and business-rule validation

### 1.2 What is out of scope

- The Django admin interface (covered by Django's own test suite)
- Third-party packages (Django, DRF, WhiteNoise, etc.)
- Infrastructure and deployment pipeline
- Browser compatibility beyond Chrome/Chromium (E2E UI phase)

---

## 2. Application under test

### 2.1 Technology stack

| Component             | Detail                                           |
| --------------------- | ------------------------------------------------ |
| Language              | Python 3.14 (local dev), 3.12 recommended for CI |
| Framework             | Django 5.1.15                                    |
| Database (local)      | SQLite 3 (file: `db.sqlite3`)                    |
| Database (production) | PostgreSQL (via `dj-database-url` + `psycopg2`)  |
| Static files          | WhiteNoise 6.6                                   |
| REST API              | Django REST Framework (Phase 2)                  |
| Package manager       | `uv`                                             |

### 2.2 Data model summary

```md
Book  ──── BookInstance (copies, loan status)
 │
 ├── Author (M2O)
 ├── Genre  (M2M)
 └── Language (FK)
```

Key business rules worth testing:

- A `BookInstance` can have status `d` (maintenance), `o` (on loan), `a` (available), or `r` (reserved)
- Renewal date must be between today and today + 4 weeks
- Only members with the `can_mark_returned` permission may mark a copy returned
- `BookInstance.is_overdue` returns `True` when `due_back < date.today()`

### 2.3 Key URLs

| Path                                   | Purpose                                                            | Auth required               |
| -------------------------------------- | ------------------------------------------------------------------ | --------------------------- |
| `/catalog/`                            | Catalogue home                                                     | No                          |
| `/catalog/books/`                      | Book list (+ `?q=` title search)                                   | No                          |
| `/catalog/book/<id>/`                  | Book detail                                                        | No                          |
| `/catalog/authors/`                    | Author list                                                        | No                          |
| `/catalog/mybooks/`                    | Borrowed books                                                     | Login required              |
| `/catalog/bookinstance/<uuid>/borrow/` | Borrow an available copy                                           | Login required (POST)       |
| `/catalog/bookinstance/<uuid>/return/` | Mark borrowed copy returned                                        | Librarian permission (POST) |
| `/catalog/book/<id>/renew/`            | Renew loan                                                         | Librarian only              |
| `/admin/`                              | Django admin                                                       | Staff/superuser             |
| `/api/`                                | DRF browsable API root                                             | Token auth (Phase 2)        |
| `/api/books/`                          | Book list — supports `?search=`, `?ordering=`                      | Token                       |
| `/api/books/<id>/`                     | Book detail                                                        | Token                       |
| `/api/authors/`                        | Author list — supports `?search=`, `?ordering=`                    | Token                       |
| `/api/authors/<id>/`                   | Author detail                                                      | Token                       |
| `/api/book-instances/`                 | Book instance list — supports `?search=`, `?status=`, `?ordering=` | Token                       |
| `/api/book-instances/<id>/`            | Book instance detail                                               | Token                       |
| `/api/genres/`                         | Genre list — supports `?search=`                                   | Token                       |
| `/api/genres/<id>/`                    | Genre detail                                                       | Token                       |
| `/api/languages/`                      | Language list — supports `?search=`                                | Token                       |
| `/api/languages/<id>/`                 | Language detail                                                    | Token                       |
| `/api/stats/`                          | Catalogue summary statistics                                       | Token                       |
| `/api/auth/token/`                     | Obtain auth token                                                  | Credentials (POST)          |

---

## 3. Testing strategy overview

The project uses a test-pyramid approach. The bulk of coverage comes from fast unit and Django-client integration tests; a smaller number of browser E2E UI tests cover critical end-to-end journeys.

```md
              ┌─────────────────┐
              │ Browser E2E UI  │  ← small count, slow, brittle if overused
              ├─────────────────┤
              │  Requests API   │  ← black-box HTTP against live test server
              ├─────────────────┤
              │ Django Client   │  ← in-process, fast, exercises views/forms
              ├─────────────────┤
              │   Unit Tests    │  ← models, forms, services — zero HTTP
              └─────────────────┘
```

Each level is tagged with a `pytest` marker so they can be run independently or together.

---

## 4. Test phases

### Phase 1 — Clean start and baseline setup

**Goal:** Establish a clean, reproducible development environment and confirm the unmodified application runs correctly.

**Completion criteria:**

- `.venv` created with `uv venv`
- All packages from `requirements.txt` installed without errors
- All 47 Django migrations applied cleanly
- Superuser account created
- Dev server responds correctly on all key URLs
- README updated with MDN attribution and project overview
- This document created
- [docs/challenge_log.md](challenge_log.md) created

**Status:** Complete (2026-04-26)

**Evidence artefacts:**

- [docs/evidence/phase-1/README.md](evidence/phase-1/README.md) — Phase 1 evidence index with embedded screenshots and verification summary
- [docs/evidence/phase-1/home-page.png](evidence/phase-1/home-page.png) — confirms the app is running and the public catalogue page loads
- [docs/evidence/phase-1/admin-dashboard.png](evidence/phase-1/admin-dashboard.png) — confirms the admin setup is functional after superuser creation
- [docs/evidence/phase-1/github-repo.png](evidence/phase-1/github-repo.png) — confirms the public repository and Phase 1 GitHub setup evidence

---

### Phase 2 — DRF REST API integration

**Goal:** Add a token-authenticated REST API surface that later API integration tests can exercise.

**Endpoints exposed:**

| Endpoint                    | Method | Auth        | Querystring support                            |
| --------------------------- | ------ | ----------- | ---------------------------------------------- |
| `/api/books/`               | GET    | Token       | `?search=`, `?ordering=`                       |
| `/api/books/<id>/`          | GET    | Token       | —                                              |
| `/api/authors/`             | GET    | Token       | `?search=`, `?ordering=`                       |
| `/api/authors/<id>/`        | GET    | Token       | —                                              |
| `/api/book-instances/`      | GET    | Token       | `?search=`, `?status=a\|o\|d\|r`, `?ordering=` |
| `/api/book-instances/<id>/` | GET    | Token       | —                                              |
| `/api/genres/`              | GET    | Token       | `?search=`                                     |
| `/api/genres/<id>/`         | GET    | Token       | —                                              |
| `/api/languages/`           | GET    | Token       | `?search=`                                     |
| `/api/languages/<id>/`      | GET    | Token       | —                                              |
| `/api/stats/`               | GET    | Token       | —                                              |
| `/api/auth/token/`          | POST   | Credentials | —                                              |

**New dependencies:** `djangorestframework==3.15.2` (added to `requirements-dev.txt`)

**Implementation:**

- `catalog/api/__init__.py` — API package marker
- `catalog/api/serializers.py` — read-only serializers for `Book`, `Author`, `BookInstance`, `Genre`, `Language`
- `catalog/api/views.py` — `ReadOnlyModelViewSet` for all five resources; `SearchFilter` and `OrderingFilter` on all viewsets; `?status=` filter param on `BookInstanceViewSet`; `catalog_stats` function view
- `catalog/api/urls.py` — `DefaultRouter` registering all five viewsets plus `/stats/` route
- `locallibrary/urls.py` — wired `/api/` include and `/api/auth/token/`
- `locallibrary/settings.py` — `rest_framework` and `rest_framework.authtoken` added to `INSTALLED_APPS`; `REST_FRAMEWORK` settings configured for token + session auth with `IsAuthenticated` default permission
- Migrations run: `authtoken` tables applied cleanly

**Status:** Complete (2026-04-27)

---

### Phase 3 — User workflow features

**Goal:** Add the features that make borrowing and returning interesting things to test.

Features:

- Catalogue search (filter by title keyword)
- Authenticated member borrow action
- Librarian return action
- Flash messages for borrow/return feedback
- Service layer (`catalog/services.py`) for reusable borrowing logic

**Implementation details:**

- `catalog/services.py` added with `borrow_book_copy()` and `return_book_copy()` to centralize borrow/return business rules and avoid duplicating status transitions in view code
- `catalog/views.py`
  - `BookListView` now supports `?q=` title search
  - new member borrow endpoint (`borrow_book`) with `login_required`
  - new librarian return endpoint (`return_book_librarian`) with `login_required` + `can_mark_returned`
  - both action endpoints now use safe `next` redirects and Django messages
- `catalog/urls.py` now includes:
  - `/catalog/bookinstance/<uuid>/borrow/`
  - `/catalog/bookinstance/<uuid>/return/`
- Templates updated:
  - `catalog/book_list.html` search UI
  - `catalog/book_detail.html` borrow action for available copies
  - `catalog/bookinstance_list.html` and `catalog/bookinstance_list_borrowed_all.html` return action for librarians
  - `base_generic.html` flash-message rendering

**Evidence artefacts:**

- [docs/evidence/phase-3/README.md](evidence/phase-3/README.md) — Phase 3 verification index and checklist

**Status:** Complete (2026-04-27)

---

### Phase 4 — Unit tests and coverage foundation

**Goal:** Achieve high coverage of models, forms, and the services layer with fast, isolated unit tests.

**Markers:** `@pytest.mark.unit`

**Coverage targets:**

| Module                | Target |
| --------------------- | ------ |
| `catalog/forms.py`    | 100%   |
| `catalog/models.py`   | 90%+   |
| `catalog/services.py` | 100%   |

**Key scenarios to cover:**

- `BookInstance.is_overdue` — past due date, future date, edge cases
- Renewal form — min boundary (today), max boundary (today + 4 weeks), outside range
- Borrow service — success path, unavailable copy path
- Return service — status reset, due-date cleared

**Run command:**

```bash
pytest -m unit --cov=catalog.forms --cov=catalog.models --cov=catalog.services \
  --cov-report=term-missing --cov-report=html:reports/coverage-html \
  --html=reports/unit-report.html --self-contained-html
```

**Execution result (2026-04-27):**

- Selected unit tests: `20 passed`, `40 deselected`
- Coverage results:
  - `catalog/forms.py`: **100%**
  - `catalog/models.py`: **100%**
  - `catalog/services.py`: **100%**
- Generated reports:
  - `reports/unit-report.html`
  - `reports/coverage-html/index.html`

**Evidence artefacts:**

- [docs/evidence/phase-4/README.md](evidence/phase-4/README.md) — Phase 4 verification summary and report links

**Status:** Complete (2026-04-28)

---

### Phase 5 — Django client integration tests

**Goal:** Exercise the full request/response cycle for all key views using Django's test client — no real HTTP, but templates render and middleware runs.

**Markers:** `@pytest.mark.integration_client`

**Coverage target:** `catalog/views.py` at 99%+

**Key scenarios:**

- Search filter returns matching books; empty query returns all
- Unauthenticated borrow attempt redirects to login
- Authenticated member borrows available copy successfully
- Borrow fails gracefully when no copies are available
- Non-librarian cannot access return endpoint (403)
- Librarian successfully marks copy returned
- Return of already-available copy triggers `BorrowWorkflowError` (exception path)
- Renewal form rejects date < today and date > today + 4 weeks
- Renewal form accepts valid date and updates due_back
- Public list/detail views render for key catalog entities
- Delete views blocked by related objects (RestrictedError)
- Index session visit counter increments on repeated visits

**Test files:**

| File | Tests |
| ----- | ----- |
| `tests/integration/client/test_search.py` | 4 |
| `tests/integration/client/test_book_detail.py` | 4 |
| `tests/integration/client/test_borrow_return.py` | 16 |
| `tests/integration/client/test_general_views.py` | 6 |
| **Total** | **30** |

**Run command:**

```bash
pytest -m integration_client \
  --cov=catalog.views \
  --cov-report=html:reports/coverage-integration-html \
  --html=reports/integration-client-report.html \
  --self-contained-html
```

**Coverage achieved:** `catalog/views.py` — **100%** (194 statements, 0 missing)

**Evidence:**

- `docs/evidence/phase-5/integration-client-report.png`
- `docs/evidence/phase-5/coverage-integration-summary.png`

**Status:** ✅ Complete — 30 passed, 0 failures, 100% views.py coverage

---

### Phase 6 — Requests-based API integration tests

**Goal:** Black-box test the DRF API endpoints over real HTTP using the `requests` library against Django's `LiveServerTestCase` or `pytest-django`'s live server fixture.

**Markers:** `@pytest.mark.integration_api`

**Key scenarios:**

- POST to `/api/auth/token/` with valid credentials → 200 + token in response body
- POST with wrong password → 400
- GET `/api/books/` without token → 401
- GET `/api/books/` with valid token → 200 + list payload with expected fields
- GET `/api/books/<id>/` → 200 + correct fields
- GET `/api/books/?search=<term>` → 200 + filtered results
- GET `/api/books/99999/` → 404
- GET `/api/authors/` with valid token → 200 + list payload
- GET `/api/authors/<id>/` → 200 + correct fields
- GET `/api/book-instances/` with valid token → 200 + list payload
- GET `/api/book-instances/?status=a` → 200 + only available instances
- GET `/api/book-instances/<id>/` → 200 + correct fields including `is_overdue`
- GET `/api/genres/` with valid token → 200 + list payload
- GET `/api/genres/<id>/` → 200 + correct fields
- GET `/api/languages/` with valid token → 200 + list payload
- GET `/api/languages/<id>/` → 200 + correct fields
- GET `/api/stats/` with valid token → 200 + expected count keys present
- GET `/api/stats/` without token → 401

**Run command:**

```bash
pytest -m integration_api --html=reports/integration-api-report.html --self-contained-html
```

**Coverage command:**

```bash
pytest -m integration_api --cov=catalog.api --cov-report=term-missing --cov-report=html:reports/coverage-integration-api-html
```

**Execution result (2026-04-28):**

- Selected integration_api tests: `18 passed`, `0 failures`, `0 skipped`
- API coverage results:
  - `catalog/api/serializers.py`: **100%**
  - `catalog/api/urls.py`: **100%**
  - `catalog/api/views.py`: **100%**
  - `catalog/api` total: **100%**

**Evidence artefacts:**

- `docs/evidence/phase-6/README.md`
- `docs/evidence/phase-6/integration-api-report.png`
- `docs/evidence/phase-6/coverage-integration-api-summary.png`
- `reports/integration-api-report.html`

**Local generated output (not committed):** `reports/coverage-integration-api-html/index.html`  
Produced by the coverage command above when run locally.

**Status:** ✅ Complete — Requests-based API integration baseline delivered

---

### Phase 7 — Browser E2E UI tests

**Goal:** Verify critical end-to-end user journeys in a real browser. These tests are gated behind a `RUN_SYSTEM_TESTS=1` environment variable so they don't run accidentally in CI.

**Markers:** `@pytest.mark.e2e_ui`

**Browser:** Chrome with Selenium Manager driver resolution (`selenium==4.25.0`)

**Page objects:**

- `BasePage` — common navigation, wait helpers
- `LoginPage`
- `CatalogPage`
- `BookDetailPage`
- `BorrowedBooksPage`
- `RenewBookPage`

**Journeys:**

1. Member logs in → searches for a known book → borrows a copy → sees it in "My Borrowed Books"
2. Librarian logs in → finds borrowed copy → marks it returned → copy no longer shows as borrowed
3. Regular member attempts to access librarian-only borrowed area (`/catalog/borrowed/`) → gets 403
4. Anonymous visitor browses home → books → book detail → authors → genres → languages
5. Librarian renews a borrowed copy with a valid date and the loan due date updates
6. Librarian renew form rejects a date more than 4 weeks ahead and re-renders with a validation error
7. Member browser GET on `/catalog/bookinstance/<uuid>/borrow/` redirects without state change
8. Librarian browser GET on `/catalog/bookinstance/<uuid>/return/` redirects without state change
9. Concurrent borrow: copy becomes unavailable after page load → click Borrow → flash error
10. Concurrent return: copy is returned after page load → click Mark returned → flash error
11. Defense-in-depth: editor direct-POSTs to `/catalog/book/<id>/delete/` for a book with copies → server `RestrictedError` handler refuses deletion with a flash error

**Run command:**

```bash
RUN_SYSTEM_TESTS=1 pytest -m e2e_ui --html=reports/e2e-ui-report.html --self-contained-html
```

**Coverage command:**

```bash
RUN_SYSTEM_TESTS=1 pytest -m e2e_ui --cov=catalog.views --cov-report=term-missing --cov-report=html:reports/coverage-e2e-ui-html
```

**Execution result (2026-04-29):**

- Selected E2E UI tests: `11 passed`, `0 failures`, `0 skipped`
- E2E UI coverage result (`catalog/views.py`): `97%` (`194 statements`, `5 missing`)
- Remaining miss is `AuthorDelete.form_valid` `RestrictedError` branch (lines 261-265), already covered by the integration-client suite (`REQ-WF-018`).

**Status:** ✅ Complete — Browser E2E UI journeys delivered (95%+ coverage on `catalog/views.py`)

---

### Phase 8 — Consolidated coverage push

**Goal:** Run the full test suite (excluding browser E2E UI tests), identify uncovered branches, and close meaningful gaps to meet aggregate targets.

**Aggregate coverage targets:**

| Area             | Target  |
| ---------------- | ------- |
| Core app logic   | 90%+    |
| Services and API | 95–100% |
| Forms            | 100%    |
| Views            | 90%+    |

**Run command:**

```bash
pytest -m "not e2e_ui" \
  --cov=catalog --cov=locallibrary \
  --cov-report=term-missing \
  --cov-report=html:reports/coverage-html \
  --cov-report=xml:reports/coverage.xml \
  --html=reports/full-test-report.html
```

**Status:** Planned

---

### Phase 9 — Final documentation and reporting

**Goal:** Ensure all documents are complete, accurate, and consistent with the actual state of the code and tests.

**Deliverables:**

- Finalised README with MDN attribution ✓ (Phase 1)
- This document, updated through Phase 8
- `docs/traceability_matrix.csv` — maps requirements to test IDs
- `docs/defect_log.csv` — records defects found during testing
- `docs/challenge_log.md` — records setup and implementation challenges
- HTML/XML coverage reports in `reports/`
- HTML test reports per phase in `reports/`

**Status:** Planned

---

## 5. Test environment

### 5.1 Local development

| Item | Detail |
| ------ | -------- |
| OS | macOS (Apple Silicon) |
| Python | 3.14.4 (via Homebrew `python@3.14`) |
| Virtual environment | `.venv` managed by `uv 0.11.6` |
| Database | SQLite (`db.sqlite3`, git-ignored) |
| Browser (Selenium) | Chrome, managed by `selenium-manager` |

### 5.2 Known compatibility constraints

See `docs/challenge_log.md` entry **CH-001** for details on the `psycopg2-binary` / Python 3.14 incompatibility. TL;DR — use `requirements.txt` for local dev (SQLite) and `requirements-prod.txt` for PostgreSQL deployments on Python ≤ 3.13.

---

## 6. Traceability

Requirements → test case mapping is maintained in `docs/traceability_matrix.csv`. This document will be updated at the conclusion of each phase.

---

## 7. Defect management

Defects discovered during testing are logged in `docs/defect_log.csv` with ID, phase, severity, description, status, and resolution. As of Phase 7, all logged defects are closed or mitigated, including browser E2E UI setup stabilization (`DEF-P7-001`).
