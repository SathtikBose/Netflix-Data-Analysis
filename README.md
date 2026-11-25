# Netflix Movies & TV Shows — Data Analysis & Interactive Dashboard

> **A beginner-friendly, production-ready data analytics portfolio project** covering Data Cleaning, Preprocessing, Exploratory Data Analysis (EDA), automated testing, Docker deployment, and an interactive Streamlit dashboard.

<!-- Screenshot placeholder -->
> **[Dashboard Screenshot Placeholder]** — *Interactive Streamlit dashboard (`app/streamlit_app.py`) with sidebar filters, KPI cards, growth trajectory, country-genre heatmap, audience maturity breakdown, and searchable catalog explorer.*

---

## Complete Beginner's Step-by-Step Guide (Zero Experience Needed)

Follow these steps in order to copy this project, make it your own, install everything, and launch the live demo on `localhost`.

### System Prerequisites (Install These First)

To run this project **without any errors**, install these two free tools on your computer before starting:

1. **Python 3.11 (Recommended: Python 3.11.9)**
   - **Why Python 3.11?** Every package in `requirements.txt` (including `pandas`, `numpy`, `pyarrow`, `matplotlib`, and `streamlit`) has pre-built installers for **Python 3.11**. Using Python 3.11 avoids compiler or wheel-build errors on Windows, macOS, and Linux. *(Python 3.12+ may work, but Python 3.11 is tested and guaranteed error-free.)*
   - Download from: [python.org/downloads/release/python-3119](https://www.python.org/downloads/release/python-3119/) (or [python.org/downloads](https://www.python.org/downloads/)).
   - **Important (Windows)**: On the first screen of the installer, **check the box `"Add Python to PATH"`** before clicking **Install Now**.
   - Verify it worked by opening PowerShell/Terminal and typing:
     ```bash
     python --version
     ```
     You should see `Python 3.11.x`.

2. **Git (Version Control Tool)**
   - Needed to download (`git clone`) the project from GitHub.
   - Download from: [git-scm.com/downloads](https://git-scm.com/downloads) (use the default installer options).
   - Verify it worked by typing:
     ```bash
     git --version
     ```

3. **A Modern Web Browser** (Chrome, Edge, Firefox, or Safari) to view the dashboard at `http://localhost:8501`.

---

### Step 1: Clone the GitHub Repository
Open **PowerShell** (Windows) or **Terminal** (macOS/Linux) and run:
```bash
git clone <your-github-repo-url>
```
*(Replace `<your-github-repo-url>` with the repository's HTTPS URL from GitHub's green **Code** button.)*

### Step 2: Open the Folder in File Explorer
Open the newly downloaded `netflix-data-analysis` folder in **Windows File Explorer** (or **Finder** on macOS).

### Step 3: Turn On Hidden Items
In **Windows File Explorer**:
1. Click the **View** tab in the top toolbar.
2. Select **Show** -> **Hidden items** (turn it **ON**).
*(On macOS Finder, press `Cmd + Shift + .` to show hidden files.)*

### Step 4: Remove the `.git` Folder (Make the Project Yours)
1. Inside the project folder, find the hidden **`.git`** folder.
2. **Delete the `.git` folder**.
   - This removes the original commit history so the project belongs completely to you.
   - *(Optional)* If you want to start your own fresh Git history later, run `git init` inside the folder.

### Step 5: Open the Project in Terminal & Create a Virtual Environment
Open **PowerShell** (or **Terminal**) inside the project folder and create an isolated **virtual environment** (a clean toolbox just for this project):

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If Windows says running scripts is disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try `.\.venv\Scripts\Activate.ps1` again.)*

**macOS / Linux (Terminal):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
You will see `(.venv)` at the start of your command line when it is active.

### Step 6: Install All Dependencies
With `(.venv)` active, run these three commands:
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e . --no-deps
```

#### What Dependencies Get Installed (`requirements.txt`)
- **Data & Math**: `pandas==2.2.3`, `numpy==2.1.3`, `pyarrow==18.1.0`
- **Charts & Visuals**: `matplotlib==3.9.2`, `seaborn==0.13.2`, `plotly==5.24.1`
- **Interactive Web Dashboard**: `streamlit==1.40.2`
- **Dataset Access & Environment**: `kaggle==1.6.17`, `python-dotenv==1.0.1`
- **Notebooks**: `jupyter==1.1.1`, `ipykernel==6.29.5`
- **Testing & Code Quality**: `pytest==8.3.4`, `pytest-cov==6.0.0`, `ruff==0.8.2`

### Step 7 (Optional): Use the Full Kaggle Dataset
The project works immediately using the included **300-row sample dataset** (`data/sample/netflix_titles_sample.csv`).
To use the full ~8,800-row catalog:
1. Download `netflix_titles.csv` from [Kaggle (`shivamb/netflix-shows`)](https://www.kaggle.com/datasets/shivamb/netflix-shows).
2. Unzip it and place `netflix_titles.csv` inside `data/raw/netflix_titles.csv`.

### Step 8: Run the Data Pipeline & Launch the Live Demo on `localhost`
1. *(Optional)* Run the full cleaning, preprocessing, and chart-generation pipeline:
   ```bash
   python -m netflix_analysis.pipeline --stage all
   ```
2. **Start the interactive dashboard**:
   ```bash
   streamlit run app/streamlit_app.py
   ```
3. Open your web browser and go to:
   **`http://localhost:8501`**
   *(To stop the server anytime, press `Ctrl + C` in the terminal.)*

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
