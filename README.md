# Netflix Movies & TV Shows — Data Analysis & Interactive Dashboard

> **A beginner-friendly, production-ready data analytics portfolio project** covering Data Cleaning, Preprocessing, Exploratory Data Analysis (EDA), automated testing, Docker deployment, and an interactive Streamlit dashboard.

<!-- Screenshot placeholder -->
> **[Dashboard Screenshot Placeholder]** — *Interactive Streamlit dashboard (`app/streamlit_app.py`) with sidebar filters, KPI cards, growth trajectory, country-genre heatmap, audience maturity breakdown, and searchable catalog explorer.*

---

## 3-Command Quick Start

Runs immediately out of the box using the included 300-row sample dataset (no Kaggle key required):

```bash
python -m venv .venv && .venv\Scripts\activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt && pip install -e . --no-deps
streamlit run app/streamlit_app.py
```

Want to generate all cleaned tables, PNG charts, and `reports/findings.md` from the CLI? Run:
```bash
python -m netflix_analysis.pipeline --stage all
```

---

## Key Features

- **Resilient Data Loading**: Uses local `data/raw/netflix_titles.csv`, falls back to Kaggle API if configured, or automatically loads `data/sample/netflix_titles_sample.csv` with clear instructions.
- **Automated Cleaning & Data Quality Report**: Repairs misplaced durations in `rating`, handles missing metadata, strips whitespace, removes true duplicates, and outputs `reports/data_quality_report.md`.
- **Smart Preprocessing**: Separates movie minutes from TV seasons, explodes multi-country and multi-genre labels for accurate attribution, and computes catalog addition lag (preserving & flagging negative lags).
- **Publication-Ready Visuals & Findings**: 8 colorblind-safe charts with plain-English `"What this tells us"` captions and data-backed `reports/findings.md`.
- **Interactive Streamlit Dashboard**: 5 sidebar filters, 6 tabs, `"How to read this chart"` beginner guides, and CSV export.
- **Plain-English Documentation**: 13 beginner-friendly guides in `docs/`.

---

## Tech Stack

- **Language**: Python 3.11+
- **Data & Math**: `pandas`, `numpy`, `pyarrow`
- **Visualization**: `matplotlib`, `seaborn`, `plotly`
- **Dashboard**: `streamlit`
- **Notebooks**: `jupyter`, `ipykernel`
- **Quality & Deployment**: `pytest`, `pytest-cov`, `ruff`, `Docker`

---

## Project Structure

```text
netflix-data-analysis/
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── Makefile                  # make setup / data / clean / eda / app / test / lint
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
├── .streamlit/
│   └── config.toml
├── data/
│   ├── raw/                  # netflix_titles.csv goes here (git-ignored)
│   ├── interim/              # Cleaned intermediate tables
│   ├── processed/            # Analysis-ready parquet/csv + exploded tables
│   └── sample/               # 300-row sample CSV (committed) so the app runs without Kaggle
├── src/netflix_analysis/
│   ├── __init__.py
│   ├── config.py             # Paths, constants, rating groups, colorblind palette
│   ├── data_loader.py        # Local -> Kaggle API -> sample fallback loader
│   ├── cleaning.py           # Nulls, whitespace, misplaced ratings, dedup, quality report
│   ├── preprocessing.py      # Duration split, lag math, exploded genre/country tables
│   ├── viz.py                # Shared chart styling and PNG export
│   ├── eda.py                # 8 EDA charts + data-backed findings.md
│   └── pipeline.py           # CLI: python -m netflix_analysis.pipeline
├── app/
│   └── streamlit_app.py      # Interactive Streamlit dashboard
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_preprocessing.ipynb
│   └── 03_eda.ipynb
├── reports/figures/          # Exported PNG charts
├── tests/                    # Unit, EDA, pipeline smoke, and Streamlit AppTest suite
└── docs/                     # Plain-English beginner documentation (00..11 + CONTRIBUTING/CHANGELOG)
```

---

## Documentation

New to data analytics? Start here: **[`docs/00_START_HERE.md`](docs/00_START_HERE.md)**.

---

## License & Dataset Attribution

- **Code License**: Released under the [MIT License](LICENSE).
- **Dataset Attribution**: Built for the Kaggle **"Netflix Movies and TV Shows"** dataset (`shivamb/netflix-shows`) curated by Shivam Bansal. Please respect Kaggle's dataset terms of use when downloading the full `netflix_titles.csv`.
