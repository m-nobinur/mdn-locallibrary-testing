# Final Report Draft - Multi-Level Automated Testing of MDN LocalLibrary

## Application under test

Application under test: MDN LocalLibrary tutorial project by Mozilla Developer Network (MDN), adapted for multi-level automated testing.

## Coverage analysis (Phase 8 consolidated run)

### Command

```bash
.venv/bin/python -m pytest -m "not e2e_ui" \
  --cov=catalog --cov=locallibrary \
  --cov-report=term-missing \
  --cov-report=html:reports/coverage-html \
  --cov-report=xml:reports/coverage.xml \
  --html=reports/full-test-report.html \
  --self-contained-html
```

### Results (2026-04-29)

- Consolidated suite outcome: `108 passed`, `11 deselected`
- Overall combined coverage (`catalog` + `locallibrary`): `97%` (`937 statements`, `32 missing`)

| Target area | Phase 8 target | Achieved |
| --- | --- | --- |
| Core app logic | 90%+ | 100% |
| Services and API | 95-100% | 100% |
| Forms | 100% | 100% |
| Views | 90%+ | 100% |

### Key module outcomes

- `catalog/forms.py`: `100%`
- `catalog/models.py`: `100%`
- `catalog/services.py`: `100%`
- `catalog/views.py`: `100%`
- `catalog/api/serializers.py`: `100%`
- `catalog/api/urls.py`: `100%`
- `catalog/api/views.py`: `100%`
