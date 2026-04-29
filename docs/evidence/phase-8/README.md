# Phase 8 Evidence - Consolidated Coverage and Maximum Coverage Push

## Commands executed

```bash
.venv/bin/python -m pytest -m "not system" \
  --cov=catalog --cov=locallibrary \
  --cov-report=term-missing \
  --cov-report=html:reports/coverage-html \
  --cov-report=xml:reports/coverage.xml \
  --html=reports/full-test-report.html \
  --self-contained-html \
  -q

.venv/bin/python -m pytest -m "not e2e_ui" \
  --cov=catalog --cov=locallibrary \
  --cov-report=term-missing \
  --cov-report=html:reports/coverage-html \
  --cov-report=xml:reports/coverage.xml \
  --html=reports/full-test-report.html \
  --self-contained-html \
  -q
```

## Result summary (2026-04-29)

- Consolidated coverage run (`not system`): `108 passed`, `11 skipped`
- Marker-aligned verification run (`not e2e_ui`): `108 passed`, `11 deselected`
- Overall combined coverage (`catalog` + `locallibrary`): `97%` (`937 statements`, `32 missing`)

### Phase-8 target verification

| Area | Target | Achieved |
| --- | --- | --- |
| Core app logic | 90%+ | 100% |
| Services and API | 95-100% | 100% |
| Forms | 100% | 100% |
| Views | 90%+ | 100% |

### Module highlights

- `catalog/forms.py`: `100%`
- `catalog/models.py`: `100%`
- `catalog/services.py`: `100%`
- `catalog/views.py`: `100%`
- `catalog/api/*`: `100%`

## Known uncovered areas with rationale

- `locallibrary/asgi.py` and `locallibrary/wsgi.py` remain uncovered in this pytest command because these deployment entry points are not imported by the in-process test workflow.
- `locallibrary/settings.py` non-covered lines are environment-conditional startup branches (`.env` presence, `DATABASE_URL` branch, and `manage.py test` compatibility paths).
- No meaningful uncovered behavior remained in core functional modules, so no additional core tests were required in this phase.

## Evidence files

- [coverage-summary.png](coverage-summary.png) - Coverage HTML summary captured from browser
- [full-test-report-summary.png](full-test-report-summary.png) - Pytest HTML full-report summary captured from browser
- [Consolidated pytest HTML report](../../../reports/full-test-report.html)
- [Consolidated coverage HTML report](../../../reports/coverage-html/index.html)
- [Consolidated coverage XML report](../../../reports/coverage.xml)

## Coverage report view

![Coverage summary](coverage-summary.png)

## Full test report view

![Full test report summary](full-test-report-summary.png)
