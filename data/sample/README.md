# Sample Dataset (`netflix_titles_sample.csv`)

This folder contains a **300-row sample dataset** (`netflix_titles_sample.csv`) that matches the exact 12-column schema of the full Kaggle **"Netflix Movies and TV Shows"** dataset (`shivamb/netflix-shows`).

## Why is this here?
- **Zero-setup demo**: Anyone can clone this repository and run the pipeline or Streamlit dashboard immediately without creating a Kaggle account or downloading files first.
- **Built-in edge cases**: The sample intentionally includes realistic data quirks (missing values, leading/trailing spaces in dates, misplaced durations in the `rating` column, negative catalog lag, and duplicate titles) so the cleaning and preprocessing tests work out of the box.

> **Note**: Numbers computed from this sample file are for demonstration and testing only. To generate real insights on the full ~8,800-row catalog, place `netflix_titles.csv` in `data/raw/` (see [`docs/04_installation_and_setup.md`](../../docs/04_installation_and_setup.md)).
