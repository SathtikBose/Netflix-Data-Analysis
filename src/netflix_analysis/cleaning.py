"""Data cleaning module for the Netflix Movies and TV Shows dataset.

Implements:
1. Misplaced value repair (moving duration values accidentally placed in ``rating``).
2. Critical null removal (dropping rows missing ``date_added`` or ``rating``).
3. Metadata null imputation (filling ``director``, ``cast``, ``country`` with ``"Unknown"``).
4. String whitespace cleanup, rating normalization, and ``date_added`` datetime parsing.
5. Deduplication on ``(title, release_year, director)``.
6. Before-vs-after Data Quality Report generation (``reports/data_quality_report.md``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from netflix_analysis.config import (
    CLEANED_DATA_CSV,
    CLEANED_DATA_PARQUET,
    CRITICAL_NON_NULL_COLUMNS,
    DATA_QUALITY_REPORT_PATH,
    NULL_FILL_COLUMNS,
    UNKNOWN_PLACEHOLDER,
    setup_logging,
)

logger = setup_logging()

# Matches misplaced duration strings in the rating column, e.g. "74 min", "1 Season"
_DURATION_IN_RATING_PATTERN = re.compile(r"^\s*\d+\s*(?:min|seasons?)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class DataQualityMetrics:
    """Snapshot of dataset quality metrics before or after cleaning."""

    row_count: int
    column_count: int
    nulls_per_column: dict[str, int]
    duplicate_count: int


@dataclass(frozen=True)
class CleaningResult:
    """Container holding the cleaned DataFrame and before/after quality metrics."""

    df: pd.DataFrame
    before: DataQualityMetrics
    after: DataQualityMetrics
    rows_filled: dict[str, int]
    rows_dropped_nulls: int
    rows_dropped_invalid_dates: int
    misplaced_ratings_fixed: int
    duplicates_removed: int


def _compute_metrics(df: pd.DataFrame) -> DataQualityMetrics:
    """Compute row count, per-column null counts, and duplicate count."""
    nulls = {col: int(df[col].isna().sum()) for col in df.columns}
    dup_subset = [c for c in ("title", "release_year", "director") if c in df.columns]
    dup_count = int(df.duplicated(subset=dup_subset, keep="first").sum()) if dup_subset else 0
    return DataQualityMetrics(
        row_count=len(df),
        column_count=len(df.columns),
        nulls_per_column=nulls,
        duplicate_count=dup_count,
    )


def _treat_blank_strings_as_na(df: pd.DataFrame) -> pd.DataFrame:
    """Convert empty or whitespace-only string cells to pandas NA."""
    cleaned = df.copy()
    object_cols = cleaned.select_dtypes(include=["object", "string"]).columns
    for col in object_cols:
        cleaned[col] = cleaned[col].replace(r"^\s*$", pd.NA, regex=True)
    return cleaned


def fix_misplaced_ratings(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Move duration values accidentally entered in ``rating`` into ``duration``.

    In the Kaggle Netflix dataset, a handful of rows have values like ``"74 min"``
    stored in ``rating`` while ``duration`` is empty. When detected, the value is
    moved to ``duration`` (if ``duration`` is currently missing) and ``rating``
    is set to ``"Unknown"``.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of ``(updated_df, count_of_fixed_rows)``.
    """
    result = df.copy()
    rating_str = result["rating"].astype("string").fillna("")
    misplaced_mask = rating_str.str.match(_DURATION_IN_RATING_PATTERN, na=False)
    fixed_count = int(misplaced_mask.sum())

    if fixed_count > 0:
        empty_duration_mask = result["duration"].isna() | (
            result["duration"].astype("string").str.strip() == ""
        )
        move_mask = misplaced_mask & empty_duration_mask
        result.loc[move_mask, "duration"] = result.loc[move_mask, "rating"].astype("string").str.strip()
        result.loc[misplaced_mask, "rating"] = UNKNOWN_PLACEHOLDER
        logger.info(
            "Fixed %d misplaced duration value(s) found in the 'rating' column.",
            fixed_count,
        )

    return result, fixed_count


def fill_metadata_nulls(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Fill missing ``director``, ``cast``, and ``country`` values with ``"Unknown"``.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of ``(updated_df, dict_of_filled_counts_per_column)``.
    """
    result = df.copy()
    filled_counts: dict[str, int] = {}
    for col in NULL_FILL_COLUMNS:
        if col in result.columns:
            missing_count = int(result[col].isna().sum())
            result[col] = result[col].fillna(UNKNOWN_PLACEHOLDER)
            filled_counts[col] = missing_count
            logger.info("Filled %d missing '%s' value(s) with '%s'.", missing_count, col, UNKNOWN_PLACEHOLDER)
    return result, filled_counts


def drop_critical_nulls(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Drop rows missing ``date_added`` or ``rating``.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of ``(updated_df, number_of_dropped_rows)``.
    """
    before_len = len(df)
    subset = [col for col in CRITICAL_NON_NULL_COLUMNS if col in df.columns]
    result = df.dropna(subset=subset).copy()
    dropped = before_len - len(result)
    logger.info(
        "Dropped %d row(s) missing critical columns (%s).",
        dropped,
        ", ".join(subset),
    )
    return result, dropped


def normalize_strings_and_dates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Strip whitespace on text columns, normalize ratings, and parse ``date_added``.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of ``(updated_df, rows_dropped_due_to_unparseable_dates)``.
    """
    result = df.copy()
    string_cols = result.select_dtypes(include=["object", "string"]).columns
    for col in string_cols:
        result[col] = result[col].astype("string").str.strip()

    # Normalize ratings (uppercase standard codes, keep "Unknown" title-cased)
    if "rating" in result.columns:
        result["rating"] = result["rating"].apply(
            lambda val: UNKNOWN_PLACEHOLDER
            if pd.isna(val) or str(val).strip().lower() == "unknown"
            else str(val).strip().upper()
        )

    # Parse date_added to datetime64[ns]
    invalid_dates = 0
    if "date_added" in result.columns:
        parsed_dates = pd.to_datetime(result["date_added"], format="mixed", errors="coerce")
        invalid_mask = parsed_dates.isna()
        invalid_dates = int(invalid_mask.sum())
        if invalid_dates > 0:
            logger.warning("Dropping %d row(s) with unparseable 'date_added'.", invalid_dates)
            result = result.loc[~invalid_mask].copy()
            parsed_dates = parsed_dates.loc[~invalid_mask]
        result["date_added"] = parsed_dates

    if "release_year" in result.columns:
        result["release_year"] = pd.to_numeric(result["release_year"], errors="coerce").astype("Int64")

    return result, invalid_dates


def deduplicate_titles(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Detect and remove duplicate titles sharing the same ``release_year`` and ``director``.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of ``(deduplicated_df, number_of_removed_duplicates)``.
    """
    dup_subset = [col for col in ("title", "release_year", "director") if col in df.columns]
    if not dup_subset:
        return df.copy(), 0

    dup_mask = df.duplicated(subset=dup_subset, keep="first")
    dup_count = int(dup_mask.sum())
    if dup_count > 0:
        sample_titles = df.loc[dup_mask, "title"].head(5).tolist()
        logger.info(
            "Detected and removed %d duplicate title(s) sharing %s. Examples: %s",
            dup_count,
            dup_subset,
            sample_titles,
        )
    else:
        logger.info("No duplicate titles detected on %s.", dup_subset)

    return df.loc[~dup_mask].reset_index(drop=True), dup_count


def clean_netflix_data(df: pd.DataFrame) -> CleaningResult:
    """Run the full data cleaning pipeline on a raw Netflix DataFrame.

    Args:
        df: Raw DataFrame loaded from CSV.

    Returns:
        :class:`CleaningResult` with cleaned DataFrame and before/after metrics.
    """
    logger.info("Starting data cleaning on %d raw rows...", len(df))
    normalized_raw = _treat_blank_strings_as_na(df)
    before_metrics = _compute_metrics(normalized_raw)

    step1, misplaced_fixed = fix_misplaced_ratings(normalized_raw)
    step2, rows_dropped_nulls = drop_critical_nulls(step1)
    step3, rows_filled = fill_metadata_nulls(step2)
    step4, invalid_dates = normalize_strings_and_dates(step3)
    cleaned_df, duplicates_removed = deduplicate_titles(step4)

    after_metrics = _compute_metrics(cleaned_df)
    logger.info(
        "Cleaning complete: %d -> %d rows.",
        before_metrics.row_count,
        after_metrics.row_count,
    )

    return CleaningResult(
        df=cleaned_df,
        before=before_metrics,
        after=after_metrics,
        rows_filled=rows_filled,
        rows_dropped_nulls=rows_dropped_nulls,
        rows_dropped_invalid_dates=invalid_dates,
        misplaced_ratings_fixed=misplaced_fixed,
        duplicates_removed=duplicates_removed,
    )


def generate_data_quality_report(
    result: CleaningResult,
    output_path: Path | None = None,
) -> Path:
    """Write a beginner-friendly before-vs-after Data Quality Report in Markdown.

    Args:
        result: :class:`CleaningResult` returned by :func:`clean_netflix_data`.
        output_path: Optional destination path; defaults to ``DATA_QUALITY_REPORT_PATH``.

    Returns:
        Path to the written Markdown report.
    """
    target = output_path or DATA_QUALITY_REPORT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Data Quality Report",
        "",
        "This report compares the Netflix dataset **before** and **after** automated cleaning.",
        "",
        "## Summary",
        "",
        "| Metric | Before Cleaning | After Cleaning | Change |",
        "| :--- | ---: | ---: | ---: |",
        f"| **Total Rows** | {result.before.row_count:,} | {result.after.row_count:,} | {result.after.row_count - result.before.row_count:+,} |",
        f"| **Total Columns** | {result.before.column_count} | {result.after.column_count} | {result.after.column_count - result.before.column_count:+d} |",
        f"| **Duplicate Titles** (`title`, `release_year`, `director`) | {result.before.duplicate_count:,} | {result.after.duplicate_count:,} | {-result.duplicates_removed:+,} |",
        "",
        "## Cleaning Actions Applied",
        "",
        f"- **Misplaced ratings repaired** (duration moved out of `rating`): **{result.misplaced_ratings_fixed:,}** row(s)",
        f"- **Rows dropped due to missing `date_added` or `rating`**: **{result.rows_dropped_nulls:,}** row(s)",
        f"- **Rows dropped due to unparseable `date_added`**: **{result.rows_dropped_invalid_dates:,}** row(s)",
        f"- **Duplicate titles removed**: **{result.duplicates_removed:,}** row(s)",
        "- **Missing metadata filled with `\"Unknown\"`**:",
    ]
    for col, count in result.rows_filled.items():
        lines.append(f"  - `{col}`: **{count:,}** value(s) filled")

    lines.extend([
        "",
        "## Null Values Per Column (Before vs. After)",
        "",
        "| Column | Nulls Before | Nulls After |",
        "| :--- | ---: | ---: |",
    ])
    for col in result.before.nulls_per_column:
        b_null = result.before.nulls_per_column.get(col, 0)
        a_null = result.after.nulls_per_column.get(col, 0)
        lines.append(f"| `{col}` | {b_null:,} | {a_null:,} |")

    lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Saved data quality report to %s", target)
    return target


def save_cleaned_data(
    df: pd.DataFrame,
    parquet_path: Path | None = None,
    csv_path: Path | None = None,
) -> tuple[Path, Path]:
    """Persist the cleaned DataFrame to Parquet and CSV in ``data/interim/``.

    Args:
        df: Cleaned DataFrame.
        parquet_path: Optional override for Parquet output path.
        csv_path: Optional override for CSV output path.

    Returns:
        Tuple of ``(parquet_path, csv_path)``.
    """
    pq_target = parquet_path or CLEANED_DATA_PARQUET
    csv_target = csv_path or CLEANED_DATA_CSV
    pq_target.parent.mkdir(parents=True, exist_ok=True)
    csv_target.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(pq_target, index=False)
    df.to_csv(csv_target, index=False)
    logger.info("Saved cleaned dataset to %s and %s", pq_target, csv_target)
    return pq_target, csv_target
