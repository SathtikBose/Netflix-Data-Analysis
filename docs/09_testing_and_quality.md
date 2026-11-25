# Testing and Code Quality

Automated tests act like a **safety net**: every time you change a line of code, tests verify that cleaning, preprocessing, chart generation, and the dashboard still work as expected.

---

## How to Run Tests & Linting

With your `.venv` active:

```bash
# Run all unit + smoke tests with a coverage report
pytest --cov=netflix_analysis --cov-report=term-missing

# Run the fast code-style & bug linter (ruff)
ruff check src tests app
```

*(With `make`: `make test` and `make lint`.)*

---

## What Is Covered

| Test File | What It Verifies |
| :--- | :--- |
| `tests/test_data_loader.py` | Project root resolution, 300-row sample schema, raw-file priority, sample fallback, and missing/invalid CSV errors. |
| `tests/test_cleaning.py` | Repairing misplaced durations in `rating`, filling `director`/`cast`/`country` nulls, dropping missing `date_added`/`rating`, whitespace stripping, deduplication, and `data_quality_report.md` generation. |
| `tests/test_preprocessing.py` | Splitting movie minutes vs. TV seasons, catalog lag math (including negative lags), comma-separated label tokenization, explode row counts, and Parquet/CSV saving. |
| `tests/test_eda_and_pipeline.py` | All 8 EDA chart functions + full-pipeline smoke test (`--stage all --prefer-sample`). |
| `tests/test_streamlit_app.py` | Streamlit `AppTest` smoke test confirming the dashboard renders 6 tabs and 4 KPIs without exceptions. |

---

## How to Add a New Test

1. Create or open a `test_*.py` file in `tests/`.
2. Write a function starting with `test_`, e.g.:
   ```python
   def test_my_new_rule() -> None:
       assert 1 + 1 == 2
   ```
3. Run `pytest` to verify it passes.
