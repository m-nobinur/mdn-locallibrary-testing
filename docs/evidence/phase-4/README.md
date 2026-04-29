# Phase 4 Evidence - Unit Testing and Coverage Foundation

## Command executed

```bash
.venv/bin/python -m pytest -m unit \
  --cov=catalog.forms \
  --cov=catalog.models \
  --cov=catalog.services \
  --cov-report=term-missing \
  --cov-report=html:reports/coverage-html \
  --html=reports/unit-report.html \
  --self-contained-html
```

## Result summary

- Test outcome: `20 passed`
- Coverage:
  - `catalog/forms.py`: `100%`
  - `catalog/models.py`: `100%`
  - `catalog/services.py`: `100%`

## Test file breakdown

| File                               | Tests | Scope                                                                         |
| ---------------------------------- | ----- | ----------------------------------------------------------------------------- |
| `tests/unit/test_models_unit.py`   | `9`   | Domain model behaviour (string methods, URLs, overdue state, display helpers) |
| `tests/unit/test_services_unit.py` | `6`   | Borrow/return service rules (state transitions, auth and duration validation) |
| `tests/unit/test_forms_unit.py`    | `5`   | Loan renewal form validation boundaries and field metadata                    |

Counts above come from `pytest -m unit --collect-only -q` and match the `20 passed` result in this phase.

## Coverage report

![Coverage files summary](coverage-files-overview.png)

## Coverage functions view

![Coverage functions summary](coverage-functions-overview.png)

## Coverage classes view

![Coverage classes summary](coverage-classes-overview.png)

## Unit report view

![Unit report summary](unit-report-overview.png)
