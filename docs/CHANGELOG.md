# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-11-25

### Added
- **Project Scaffold & Data Loader**: Relative-path `config.py`, pinned `requirements.txt`, `Makefile`, MIT `LICENSE`, 300-row sample CSV, and `data_loader.py` (local -> Kaggle API -> sample fallback).
- **Data Cleaning**: Misplaced duration repair in `rating`, critical null removal, metadata `"Unknown"` imputation, whitespace & date normalization, deduplication, and `reports/data_quality_report.md`.
- **Preprocessing**: `Movie_Duration_Min` / `TV_Seasons_Count` split, `Addition_Lag_Years` & `Catalog_Category` with explicit negative-lag handling, and exploded `titles_by_genre` & `titles_by_country` Parquet tables.
- **Exploratory Data Analysis**: 8 colorblind-safe PNG charts (4 core + 4 `[Extra]` charts), data-backed `reports/findings.md`, and 3 Jupyter walkthrough notebooks.
- **Interactive Dashboard**: Streamlit app (`app/streamlit_app.py`) with 5 sidebar filters, 6 tabs, beginner-friendly `"How to read this chart"` expanders, CSV export, and sample-mode banner.
- **Deployment & Documentation**: `Dockerfile`, `.streamlit/config.toml`, and 13 plain-English beginner guides in `docs/`.
