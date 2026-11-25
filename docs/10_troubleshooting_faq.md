# Troubleshooting & FAQ

Stuck on an error? Check the table below first.

---

## Common Errors & Fixes

| Symptom / Error | Cause | Fix |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'netflix_analysis'` | Virtual environment isn't active or package wasn't installed in editable mode | Activate `.venv`, then run `pip install -e . --no-deps`. |
| Dashboard shows **"Sample Mode Active"** | `data/raw/netflix_titles.csv` is not present and Kaggle credentials aren't set | Download `netflix_titles.csv` from Kaggle and place it in `data/raw/netflix_titles.csv`, then refresh. |
| `FileNotFoundError: Cleaned dataset not found` | You ran `--stage preprocess` before `--stage clean` | Run `python -m netflix_analysis.pipeline --stage all` instead. |
| `streamlit: command not found` | `.venv` is not activated | Run `.\.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (macOS/Linux). |
| Charts look different from blog posts about Netflix | You are viewing the 300-row sample dataset | Add the full ~8,800-row `netflix_titles.csv` to `data/raw/` and re-run the pipeline. |

---

## Frequently Asked Questions (FAQ)

**Q: Do I need a Kaggle account to run this project?**
No! The repository includes a 300-row sample dataset (`data/sample/netflix_titles_sample.csv`) so the pipeline, tests, notebooks, and Streamlit dashboard all work immediately offline.

**Q: Why is `data/raw/netflix_titles.csv` ignored by Git?**
It is good practice never to redistribute large third-party datasets inside your code repository. Users download it themselves from Kaggle (or use the sample).

**Q: Why do country counts add up to more than the total number of titles?**
Because many titles are international co-productions (e.g., `"United States, United Kingdom"`). We **explode** multi-country cells so every participating country gets credit.

**Q: Why are there negative numbers in `Addition_Lag_Years`?**
In a small number of rows, `Year_Added` is 1 year earlier than `release_year` due to regional premiere or season-update metadata in the source data. We preserve and flag these rows transparently.
