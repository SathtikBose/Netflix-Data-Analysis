# Netflix Movies & TV Shows — Data Analysis & Interactive Dashboard

> **A beginner-friendly, production-ready data analytics portfolio project** covering Data Cleaning, Preprocessing, Exploratory Data Analysis (EDA), automated testing, and an interactive Streamlit dashboard.

<!-- Screenshot placeholder (will be updated with real dashboard/chart screenshots) -->
> **[Dashboard Screenshot Placeholder]** — *Interactive Streamlit dashboard with sidebar filters, KPI cards, growth charts, country/genre heatmaps, and searchable catalog explorer.*

---

## 3-Command Quick Start

Works out of the box using the included 300-row sample dataset (no Kaggle key required):

```bash
python -m venv .venv && .venv\Scripts\activate   # On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt && pip install -e . --no-deps
python -m netflix_analysis.data_loader
```

*(Full pipeline & dashboard commands will be added as Phases 2–5 are completed.)*

---

## Key Features

- **Resilient Data Loading**: Uses local `data/raw/netflix_titles.csv`, falls back to Kaggle API if configured, or automatically loads `data/sample/netflix_titles_sample.csv` with clear instructions.
- **Automated Cleaning & Data Quality Report**: Handles missing metadata, strips whitespace, fixes misplaced duration values in the rating column, removes true duplicates, and outputs a before/after report.
- **Smart Preprocessing**: Separates movie minutes from TV seasons, explodes multi-country and multi-genre labels for accurate attribution, and computes catalog addition lag.
- **Publication-Ready Visuals & Findings**: Colorblind-safe charts with plain-English captions and data-backed findings.
- **Interactive Streamlit Dashboard**: Explore the catalog with point-and-click filters and CSV export.

---

## Tech Stack

- **Language**: Python 3.11+
- **Data & Math**: `pandas`, `numpy`, `pyarrow`
- **Visualization**: `matplotlib`, `seaborn`, `plotly`
- **Dashboard**: `streamlit`
- **Notebooks**: `jupyter`, `ipykernel`
- **Quality & Testing**: `pytest`, `pytest-cov`, `ruff`

---

## Project Structure

```text
netflix-data-analysis/
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── Makefile                  # make setup / data / clean / eda / app / test
├── .gitignore
├── .env.example
├── Dockerfile                # Added in Phase 6
├── data/
│   ├── raw/                  # netflix_titles.csv goes here (git-ignored)
│   ├── interim/              # Cleaned intermediate tables
│   ├── processed/            # Analysis-ready parquet/csv + exploded tables
│   └── sample/               # 300-row sample CSV (committed) so the app runs without Kaggle
├── src/netflix_analysis/
│   ├── __init__.py
│   ├── config.py             # Paths, constants, rating groups, palette
│   ├── data_loader.py        # Local -> Kaggle API -> sample fallback loader
│   ├── cleaning.py           # Phase 2
│   ├── preprocessing.py      # Phase 3
│   ├── eda.py                # Phase 4
│   ├── viz.py                # Phase 4
│   └── pipeline.py           # Phase 2-4 CLI orchestrator
├── app/
│   └── streamlit_app.py      # Phase 5
├── notebooks/                # Phase 4
├── reports/figures/          # Exported PNG charts
├── tests/                    # Unit & smoke tests
└── docs/                     # Plain-English beginner documentation
```

---

## Documentation

New to data analytics? Start here: **[`docs/00_START_HERE.md`](docs/00_START_HERE.md)**.

---

## License & Dataset Attribution

- **Code License**: Released under the [MIT License](LICENSE).
- **Dataset Attribution**: Built for the Kaggle **"Netflix Movies and TV Shows"** dataset (`shivamb/netflix-shows`) curated by Shivam Bansal. Please respect Kaggle's dataset terms of use when downloading the full `netflix_titles.csv`.
