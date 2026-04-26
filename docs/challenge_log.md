# Challenge Log — MDN LocalLibrary Automated Testing Project

This log records every significant obstacle, version conflict, or unexpected behaviour encountered during the project — along with what was tried, what eventually worked, and what anyone picking up this repo should know before they waste an afternoon on the same thing.

Entries follow this template:

```md
## CH-NNN — <short title>
- **Date:** YYYY-MM-DD
- **Phase:** Phase N
- **Severity:** High / Medium / Low
- **Symptom:** What went wrong or looked wrong
- **Root cause:** Why it happened
- **Investigation:** What was tried to understand or fix it
- **Resolution:** What actually resolved it
- **Impact:** What would have broken if left unresolved
- **Lesson learned:** One-line takeaway
```

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

### Lesson learned

Check `runtime.txt` before creating your `.venv` — if the pinned runtime differs significantly from the host Python, use `uv venv .venv --python <version>` to align them. And always check whether a C-extension package has wheels for your CPython version before assuming `pip install` will just work.

---

## CH-002 — Phase 2 completed without blocking challenges

- **Date:** 2026-04-26
- **Phase:** Phase 2
- **Severity:** N/A

### Summary

Phase 2 DRF integration completed cleanly. No blocking issues were encountered during dependency installation, settings configuration, serializer/viewset implementation, migration, or URL resolution verification.

---

## CH-003 — (placeholder for next challenge)

*To be completed when the next challenge arises.*

---
