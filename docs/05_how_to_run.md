# How to Run the Project

There are **three ways** to use this project depending on your goal. Pick whichever fits you best!

> Make sure your virtual environment (`.venv`) is active before running any command (see [`04_installation_and_setup.md`](04_installation_and_setup.md)).

---

## Way 1: Launch the Interactive Dashboard Only (Zero Code)

If you just want to click around, filter titles, and explore charts in your browser:

```bash
streamlit run app/streamlit_app.py
```
*(Or with Make: `make app`)*

**Expected Output:**
- Your terminal will print a local URL (usually `http://localhost:8501`) and open a browser tab automatically.
- If you haven't downloaded the full Kaggle CSV, you will see an amber **Sample Mode Active** banner at the top letting you know it's using the 300-row sample.
- Use the left sidebar to filter by **Type**, **Release Year**, **Country**, **Genre**, and **Maturity Rating**.

---

## Way 2: Run the Full Automated Pipeline (CLI)

If you want to generate all cleaned tables, processed Parquet/CSV files, PNG charts, and Markdown reports:

```bash
python -m netflix_analysis.pipeline --stage all
```
*(Or with Make: `make eda`)*

You can also run individual stages:
- **Cleaning only**: `python -m netflix_analysis.pipeline --stage clean`
- **Preprocessing only** (requires clean stage first): `python -m netflix_analysis.pipeline --stage preprocess`
- **EDA charts & findings only** (requires preprocess stage first): `python -m netflix_analysis.pipeline --stage eda`
- **Force sample mode** even if `data/raw/netflix_titles.csv` exists: add `--prefer-sample`.

**Expected Output:**
1. `data/interim/netflix_cleaned.parquet` & `.csv`
2. `reports/data_quality_report.md` (before vs. after row & null counts)
3. `data/processed/netflix_processed.parquet` & `.csv`
4. `data/processed/titles_by_genre.parquet` & `titles_by_country.parquet`
5. 8 PNG charts in `reports/figures/`
6. `reports/findings.md` (data-backed summary)

---

## Way 3: Step-by-Step Jupyter Notebooks (Learning Mode)

If you want to read explanations and run code one cell at a time:

```bash
jupyter lab
```
*(Or `jupyter notebook`)*

Open the `notebooks/` folder in order:
1. `notebooks/01_data_cleaning.ipynb` — inspect raw nulls and watch the cleaner work.
2. `notebooks/02_preprocessing.ipynb` — see duration splitting, lag math, and exploded tables.
3. `notebooks/03_eda.ipynb` — render the charts interactively inside the notebook.

**Expected Output:**
- Each notebook cell prints summary tables or displays charts directly beneath the code.
