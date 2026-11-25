"""Central configuration for paths, constants, and domain mappings.

All file paths are resolved relative to the repository root (or an optional
environment variable override) so the project never relies on hard-coded
machine-specific paths.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root & directory layout
# ---------------------------------------------------------------------------
# src/netflix_analysis/config.py -> parents[2] is the repository root.
PROJECT_ROOT: Path = Path(
    os.environ.get("NETFLIX_PROJECT_ROOT", Path(__file__).resolve().parents[2])
)

DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
INTERIM_DATA_DIR: Path = DATA_DIR / "interim"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
SAMPLE_DATA_DIR: Path = DATA_DIR / "sample"

REPORTS_DIR: Path = PROJECT_ROOT / "reports"
FIGURES_DIR: Path = REPORTS_DIR / "figures"

# ---------------------------------------------------------------------------
# Standard file paths
# ---------------------------------------------------------------------------
RAW_DATASET_FILENAME: str = "netflix_titles.csv"
SAMPLE_DATASET_FILENAME: str = "netflix_titles_sample.csv"

RAW_DATASET_PATH: Path = RAW_DATA_DIR / RAW_DATASET_FILENAME
SAMPLE_DATASET_PATH: Path = SAMPLE_DATA_DIR / SAMPLE_DATASET_FILENAME

CLEANED_DATA_PARQUET: Path = INTERIM_DATA_DIR / "netflix_cleaned.parquet"
CLEANED_DATA_CSV: Path = INTERIM_DATA_DIR / "netflix_cleaned.csv"

PROCESSED_DATA_PARQUET: Path = PROCESSED_DATA_DIR / "netflix_processed.parquet"
PROCESSED_DATA_CSV: Path = PROCESSED_DATA_DIR / "netflix_processed.csv"
TITLES_BY_GENRE_PARQUET: Path = PROCESSED_DATA_DIR / "titles_by_genre.parquet"
TITLES_BY_COUNTRY_PARQUET: Path = PROCESSED_DATA_DIR / "titles_by_country.parquet"

DATA_QUALITY_REPORT_PATH: Path = REPORTS_DIR / "data_quality_report.md"
FINDINGS_REPORT_PATH: Path = REPORTS_DIR / "findings.md"

# ---------------------------------------------------------------------------
# Kaggle dataset identifier
# ---------------------------------------------------------------------------
KAGGLE_DATASET_SLUG: str = "shivamb/netflix-shows"

# ---------------------------------------------------------------------------
# Dataset schema & domain constants
# ---------------------------------------------------------------------------
EXPECTED_COLUMNS: tuple[str, ...] = (
    "show_id",
    "type",
    "title",
    "director",
    "cast",
    "country",
    "date_added",
    "release_year",
    "rating",
    "duration",
    "listed_in",
    "description",
)

UNKNOWN_PLACEHOLDER: str = "Unknown"
NULL_FILL_COLUMNS: tuple[str, ...] = ("director", "cast", "country")
CRITICAL_NON_NULL_COLUMNS: tuple[str, ...] = ("date_added", "rating")

# Maturity rating groupings for beginner-friendly audience profiling
RATING_AUDIENCE_GROUPS: dict[str, str] = {
    "TV-Y": "Kids",
    "TV-Y7": "Kids",
    "TV-Y7-FV": "Kids",
    "G": "Kids",
    "TV-G": "Kids",
    "PG": "Older Kids / Family",
    "TV-PG": "Older Kids / Family",
    "PG-13": "Teens",
    "TV-14": "Teens",
    "R": "Adults",
    "TV-MA": "Adults",
    "NC-17": "Adults",
    "NR": "Unrated / Unknown",
    "UR": "Unrated / Unknown",
    "Unknown": "Unrated / Unknown",
}

# Colorblind-safe Okabe-Ito inspired palette
COLOR_PALETTE: dict[str, str] = {
    "movie": "#0072B2",      # Blue
    "tv_show": "#D55E00",    # Vermilion / Orange-Red
    "accent": "#009E73",     # Bluish Green
    "neutral": "#56B4E9",    # Sky Blue
    "muted": "#7F7F7F",      # Gray
    "highlight": "#E69F00",  # Orange
    "purple": "#CC79A7",     # Reddish Purple
}


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the package-wide logger.

    Args:
        level: Standard logging level (e.g., logging.INFO or logging.DEBUG).

    Returns:
        Configured ``netflix_analysis`` logger instance.
    """
    logger = logging.getLogger("netflix_analysis")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
