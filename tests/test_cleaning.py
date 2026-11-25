"""Unit tests for the data cleaning module."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from netflix_analysis.cleaning import (
    clean_netflix_data,
    deduplicate_titles,
    drop_critical_nulls,
    fill_metadata_nulls,
    fix_misplaced_ratings,
    generate_data_quality_report,
    normalize_strings_and_dates,
)
from netflix_analysis.data_loader import load_netflix_data


def _sample_row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "show_id": "s1",
        "type": "Movie",
        "title": "Sample Title",
        "director": "Jane Doe",
        "cast": "Actor One",
        "country": "United States",
        "date_added": "January 15, 2021",
        "release_year": 2020,
        "rating": "PG-13",
        "duration": "100 min",
        "listed_in": "Dramas",
        "description": "A sample description.",
    }
    base.update(overrides)
    return base


def test_fix_misplaced_ratings_moves_duration_and_sets_unknown() -> None:
    """Misplaced duration in rating should move to empty duration and set rating='Unknown'."""
    df = pd.DataFrame([_sample_row(rating="74 min", duration=pd.NA)])
    fixed_df, count = fix_misplaced_ratings(df)
    assert count == 1
    assert fixed_df.loc[0, "duration"] == "74 min"
    assert fixed_df.loc[0, "rating"] == "Unknown"


def test_fill_metadata_nulls_fills_director_cast_country() -> None:
    """Missing director, cast, and country should be filled with 'Unknown'."""
    df = pd.DataFrame([_sample_row(director=pd.NA, cast=pd.NA, country=pd.NA)])
    filled_df, counts = fill_metadata_nulls(df)
    assert filled_df.loc[0, "director"] == "Unknown"
    assert filled_df.loc[0, "cast"] == "Unknown"
    assert filled_df.loc[0, "country"] == "Unknown"
    assert counts == {"director": 1, "cast": 1, "country": 1}


def test_drop_critical_nulls_drops_missing_date_or_rating() -> None:
    """Rows missing date_added or rating should be dropped."""
    df = pd.DataFrame(
        [
            _sample_row(show_id="s1"),
            _sample_row(show_id="s2", date_added=pd.NA),
            _sample_row(show_id="s3", rating=pd.NA),
        ]
    )
    kept_df, dropped = drop_critical_nulls(df)
    assert dropped == 2
    assert list(kept_df["show_id"]) == ["s1"]


def test_normalize_strings_and_dates_strips_whitespace_and_parses_date() -> None:
    """Leading/trailing whitespace in date_added should be stripped before parsing."""
    df = pd.DataFrame([_sample_row(date_added="  September 9, 2021  ", rating=" tv-ma ")])
    norm_df, invalid = normalize_strings_and_dates(df)
    assert invalid == 0
    assert pd.api.types.is_datetime64_any_dtype(norm_df["date_added"])
    assert norm_df.loc[0, "date_added"] == pd.Timestamp("2021-09-09")
    assert norm_df.loc[0, "rating"] == "TV-MA"


def test_deduplicate_titles_removes_same_title_year_director() -> None:
    """Duplicate titles sharing release_year and director should be removed."""
    df = pd.DataFrame(
        [
            _sample_row(show_id="s1", title="Twin Film", release_year=2020, director="Director A"),
            _sample_row(show_id="s2", title="Twin Film", release_year=2020, director="Director A"),
            _sample_row(show_id="s3", title="Twin Film", release_year=2021, director="Director A"),
        ]
    )
    dedup_df, removed = deduplicate_titles(df)
    assert removed == 1
    assert list(dedup_df["show_id"]) == ["s1", "s3"]


def test_clean_netflix_data_on_sample_and_report(tmp_path: Path) -> None:
    """Full cleaning on the 300-row sample should fix quirks and write a report."""
    loaded = load_netflix_data(prefer_sample=True)
    result = clean_netflix_data(loaded.df)

    assert result.before.row_count == 300
    assert result.misplaced_ratings_fixed == 2
    assert result.rows_dropped_nulls == 3
    assert result.duplicates_removed == 1
    assert result.after.row_count == 296
    assert result.after.duplicate_count == 0
    assert all(count == 0 for count in result.after.nulls_per_column.values())

    report_path = tmp_path / "data_quality_report.md"
    written = generate_data_quality_report(result, output_path=report_path)
    assert written.is_file()
    content = written.read_text(encoding="utf-8")
    assert "Data Quality Report" in content
    assert "300" in content
    assert "296" in content
