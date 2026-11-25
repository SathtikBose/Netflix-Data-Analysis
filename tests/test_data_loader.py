"""Unit tests for configuration and dataset loading."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from netflix_analysis.config import (
    EXPECTED_COLUMNS,
    PROJECT_ROOT,
    SAMPLE_DATASET_PATH,
)
from netflix_analysis.data_loader import load_netflix_data, validate_schema


def test_project_root_exists() -> None:
    """PROJECT_ROOT should point to the repository directory."""
    assert PROJECT_ROOT.is_dir()
    assert (PROJECT_ROOT / "src" / "netflix_analysis").is_dir()


def test_sample_dataset_exists_and_has_300_rows() -> None:
    """Committed sample CSV should exist, contain 300 rows, and match schema."""
    assert SAMPLE_DATASET_PATH.is_file()
    result = load_netflix_data(prefer_sample=True)
    assert result.source == "sample"
    assert len(result.df) == 300
    assert tuple(result.df.columns) == EXPECTED_COLUMNS


def test_load_netflix_data_prefers_local_raw(tmp_path: Path) -> None:
    """When a valid raw CSV exists, load_netflix_data should return source='raw'."""
    raw_file = tmp_path / "netflix_titles.csv"
    pd.DataFrame(
        [
            {
                "show_id": "s1",
                "type": "Movie",
                "title": "Test Movie",
                "director": "Test Director",
                "cast": "Actor A",
                "country": "United States",
                "date_added": "January 1, 2021",
                "release_year": 2020,
                "rating": "PG-13",
                "duration": "100 min",
                "listed_in": "Dramas",
                "description": "A test movie.",
            }
        ]
    ).to_csv(raw_file, index=False)

    result = load_netflix_data(raw_path=raw_file, allow_kaggle=False)
    assert result.source == "raw"
    assert result.path == raw_file
    assert len(result.df) == 1


def test_load_netflix_data_falls_back_to_sample(tmp_path: Path) -> None:
    """When raw CSV is missing and Kaggle is disabled, fall back to sample."""
    missing_raw = tmp_path / "does_not_exist.csv"
    result = load_netflix_data(
        raw_path=missing_raw,
        sample_path=SAMPLE_DATASET_PATH,
        allow_kaggle=False,
    )
    assert result.source == "sample"
    assert len(result.df) == 300


def test_load_netflix_data_raises_when_no_files_exist(tmp_path: Path) -> None:
    """Raise FileNotFoundError if neither raw nor sample CSV exists."""
    with pytest.raises(FileNotFoundError):
        load_netflix_data(
            raw_path=tmp_path / "missing_raw.csv",
            sample_path=tmp_path / "missing_sample.csv",
            allow_kaggle=False,
        )


def test_validate_schema_rejects_missing_columns(tmp_path: Path) -> None:
    """validate_schema should raise ValueError if required columns are missing."""
    bad_df = pd.DataFrame({"show_id": ["s1"], "title": ["Only Two Columns"]})
    with pytest.raises(ValueError, match="missing expected columns"):
        validate_schema(bad_df, tmp_path / "bad.csv")


def test_validate_schema_rejects_empty_dataframe(tmp_path: Path) -> None:
    """validate_schema should raise ValueError for an empty DataFrame."""
    empty_df = pd.DataFrame(columns=list(EXPECTED_COLUMNS))
    with pytest.raises(ValueError, match="empty"):
        validate_schema(empty_df, tmp_path / "empty.csv")
