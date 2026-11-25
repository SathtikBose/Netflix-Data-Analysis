# Installation and Setup Guide

Follow this step-by-step guide to set up the project on **Windows**, **macOS**, or **Linux**. You do **not** need prior Python experience.

> **Good news**: You can run the entire project right away using the built-in 300-row sample dataset. Setting up a Kaggle account is **optional** (only needed if you want the full ~8,800-row dataset).

---

## Step 1: Install Python 3.11+

Check if Python is already installed by opening a terminal (PowerShell on Windows, Terminal on macOS/Linux) and running:

```bash
python --version
# or on macOS/Linux:
python3 --version
```

If you see `Python 3.11.x` or newer, skip to **Step 2**. Otherwise:
- **Windows**: Download Python 3.11+ from [python.org/downloads](https://www.python.org/downloads/). During installation, **check the box that says "Add Python to PATH"**.
- **macOS**: Install via [python.org](https://www.python.org/downloads/) or Homebrew: `brew install python@3.11`.
- **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip`.

---

## Step 2: Download (Clone) This Project

```bash
git clone <your-repo-url>
cd netflix-data-analysis
```

*(If you downloaded a ZIP file instead of using `git`, unzip it and `cd` into the folder.)*

---

## Step 3: Create a Virtual Environment

A **virtual environment** is like a clean, isolated toolbox just for this project so its packages never clash with anything else on your computer.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You will know it worked when `(.venv)` appears at the start of your terminal prompt.

---

## Step 4: Install Dependencies

With `(.venv)` active, run:

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e . --no-deps
```

*(If you have `make` installed on macOS/Linux/Git Bash, you can simply run `make setup`.)*

---

## Step 5 (Optional): Get the Full ~8,800-Row Kaggle Dataset

Without this step, the project automatically uses `data/sample/netflix_titles_sample.csv` (300 rows). To use the full dataset, pick **either Option A (easiest) or Option B (automated)**:

### Option A: Manual Download (No API Key Needed)
1. Create a free account at [kaggle.com](https://www.kaggle.com).
2. Visit [kaggle.com/datasets/shivamb/netflix-shows](https://www.kaggle.com/datasets/shivamb/netflix-shows) and click **Download**.
3. Unzip the downloaded archive to get `netflix_titles.csv`.
4. Move `netflix_titles.csv` into `data/raw/netflix_titles.csv`.

### Option B: Automatic Download via Kaggle API
1. Log in to [kaggle.com](https://www.kaggle.com) -> **Settings** -> **API** -> **Create New Token**. This downloads `kaggle.json`.
2. Choose **one** way to store your credentials:
   - **Using `.env` (recommended for this project)**: Copy `.env.example` to `.env` and fill in your `KAGGLE_USERNAME` and `KAGGLE_KEY` from `kaggle.json`.
   - **Using `~/.kaggle/kaggle.json`**:
     - Windows: `C:\Users\<YourName>\.kaggle\kaggle.json`
     - macOS/Linux: `~/.kaggle/kaggle.json` (run `chmod 600 ~/.kaggle/kaggle.json`)
3. Run `python -m netflix_analysis.data_loader` to download automatically.

> **Security Reminder**: Never commit `.env`, `kaggle.json`, or `data/raw/netflix_titles.csv` to Git. They are already listed in `.gitignore`.

---

## Troubleshooting Table

| Problem | Likely Cause | How to Fix |
| :--- | :--- | :--- |
| `'python' is not recognized` (Windows) | Python wasn't added to PATH | Re-run Python installer and check **"Add Python to PATH"**, or try `py -3.11`. |
| `Activate.ps1 cannot be loaded because running scripts is disabled` (Windows) | PowerShell execution policy | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again. |
| `ModuleNotFoundError: No module named 'netflix_analysis'` | Package not installed in editable mode | Activate `.venv` and run `pip install -e . --no-deps`. |
| `KaggleApi` 401/403 error | Invalid or expired Kaggle token | Re-download `kaggle.json` from Kaggle Settings -> API, or use Option A (manual download). |
| `make: command not found` (Windows) | `make` is not installed by default on Windows | Run the `python -m ...` or `pytest` commands directly instead of `make`. |
