"""Data preprocessing and feature engineering for the Netflix dataset.

Implements:
1. Duration unit separation (``Movie_Duration_Min`` and ``TV_Seasons_Count``).
2. Catalog lag calculation (``Year_Added``, ``Addition_Lag_Years``, ``Catalog_Category``)
   with explicit handling and logging of negative lags.
3. Audience group & release decade enrichment for downstream EDA.
4. Multi-label tokenization and explosion into ``titles_by_genre`` and
   ``titles_by_country`` tables.
5. Persistence of processed outputs to ``data/processed/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from netflix_analysis.config import (
    PROCESSED_DATA_CSV,
    PROCESSED_DATA_PARQUET,
    RATING_AUDIENCE_GROUPS,
    TITLES_BY_COUNTRY_PARQUET,
    TITLES_BY_GENRE_PARQUET,
    UNKNOWN_PLACEHOLDER,
    setup_logging,
)

logger = setup_logging()


@dataclass(frozen=True)
class PreprocessingResult:
    """Container holding the processed main DataFrame and exploded tables."""

    df: pd.DataFrame
    titles_by_genre: pd.DataFrame
    titles_by_country: pd.DataFrame
    negative_lag_count: int


def split_duration_units(df: pd.DataFrame) -> pd.DataFrame:
    """Split ``duration`` into ``Movie_Duration_Min`` and ``TV_Seasons_Count``.

    Movies receive an integer minute count in ``Movie_Duration_Min`` and ``<NA>``
    in ``TV_Seasons_Count``; TV Shows receive the opposite.

    Args:
        df: Cleaned DataFrame containing ``type`` and ``duration`` columns.

    Returns:
        Copy of ``df`` with ``Movie_Duration_Min`` and ``TV_Seasons_Count`` added.
    """
    result = df.copy()
    extracted_num = pd.to_numeric(
        result["duration"].astype("string").str.extract(r"(\d+)", expand=False),
        errors="coerce",
    ).astype("Int64")

    is_movie = result["type"].astype("string").str.strip().str.lower() == "movie"
    is_tv = result["type"].astype("string").str.strip().str.lower() == "tv show"

    result["Movie_Duration_Min"] = extracted_num.where(is_movie, pd.NA).astype("Int64")
    result["TV_Seasons_Count"] = extracted_num.where(is_tv, pd.NA).astype("Int64")
    return result


def add_catalog_lag_features(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Compute ``Year_Added``, ``Month_Added``, ``Addition_Lag_Years``, and ``Catalog_Category``.

    Categorizes titles into:
    - ``"New / Original (0-1 yr)"``: added within 0 to 1 year of release
    - ``"Older Licensed (2+ yrs)"``: added 2 or more years after release
    - ``"Negative Lag (<0 yr)"``: ``Year_Added < release_year`` (explicitly preserved & logged)

    Args:
        df: DataFrame with parsed ``date_added`` and numeric ``release_year``.

    Returns:
        Tuple of ``(updated_df, negative_lag_count)``.
    """
    result = df.copy()
    date_series = pd.to_datetime(result["date_added"], errors="coerce")

    result["Year_Added"] = date_series.dt.year.astype("Int64")
    result["Month_Added"] = date_series.dt.month.astype("Int64")
    result["Month_Added_Name"] = date_series.dt.month_name().astype("string")

    release_year = pd.to_numeric(result["release_year"], errors="coerce").astype("Int64")
    result["Addition_Lag_Years"] = (result["Year_Added"] - release_year).astype("Int64")

    negative_mask = result["Addition_Lag_Years"] < 0
    negative_count = int(negative_mask.sum())
    if negative_count > 0:
        logger.info(
            "Found %d title(s) with negative Addition_Lag_Years (Year_Added < release_year). "
            "Preserving and flagging as 'Negative Lag (<0 yr)'.",
            negative_count,
        )

    def _categorize_lag(lag: object) -> str:
        if pd.isna(lag):
            return UNKNOWN_PLACEHOLDER
        lag_int = int(lag)
        if lag_int < 0:
            return "Negative Lag (<0 yr)"
        if lag_int <= 1:
            return "New / Original (0-1 yr)"
        return "Older Licensed (2+ yrs)"

    result["Catalog_Category"] = result["Addition_Lag_Years"].apply(_categorize_lag)
    result["Is_Original_Window"] = result["Addition_Lag_Years"].between(0, 1).fillna(False)

    # Enrichment for EDA: Release_Decade and Audience_Group
    result["Release_Decade"] = (
        ((release_year // 10) * 10).astype("string") + "s"
    )
    result["Audience_Group"] = (
        result["rating"]
        .astype("string")
        .map(RATING_AUDIENCE_GROUPS)
        .fillna("Unrated / Unknown")
    )
    return result, negative_count


def tokenize_csv_labels(series: pd.Series) -> pd.Series:
    """Split comma-separated string values into clean, stripped lists of labels.

    Args:
        series: Pandas Series containing comma-separated text (e.g., genres or countries).

    Returns:
        Series of ``list[str]`` with whitespace stripped and empty tokens removed.
    """
    def _split_item(value: object) -> list[str]:
        if pd.isna(value):
            return [UNKNOWN_PLACEHOLDER]
        tokens = [part.strip() for part in str(value).split(",") if part.strip()]
        return tokens if tokens else [UNKNOWN_PLACEHOLDER]

    return series.apply(_split_item)


def build_exploded_table(
    df: pd.DataFrame,
    source_col: str,
    target_col: str,
) -> pd.DataFrame:
    """Explode a comma-separated multi-label column into one row per label.

    Args:
        df: Preprocessed DataFrame.
        source_col: Column to tokenize and explode (e.g., ``"listed_in"`` or ``"country"``).
        target_col: Name of the resulting single-label column (e.g., ``"genre"`` or ``"country"``).

    Returns:
        Exploded DataFrame with one row per ``(show_id, label)`` pair.
    """
    working = df.copy()
    working[target_col] = tokenize_csv_labels(working[source_col])
    exploded = working.explode(target_col, ignore_index=True)
    exploded[target_col] = exploded[target_col].astype("string").str.strip()
    return exploded


def preprocess_netflix_data(df: pd.DataFrame) -> PreprocessingResult:
    """Run the full preprocessing pipeline on a cleaned Netflix DataFrame.

    Args:
        df: Cleaned DataFrame from :func:`netflix_analysis.cleaning.clean_netflix_data`.

    Returns:
        :class:`PreprocessingResult` containing the main DataFrame and exploded tables.
    """
    logger.info("Starting preprocessing on %d cleaned rows...", len(df))
    step1 = split_duration_units(df)
    step2, negative_lag_count = add_catalog_lag_features(step1)

    titles_by_genre = build_exploded_table(step2, source_col="listed_in", target_col="genre")
    titles_by_country = build_exploded_table(step2, source_col="country", target_col="country")

    logger.info(
        "Preprocessing complete: %d main rows | %d genre rows | %d country rows.",
        len(step2),
        len(titles_by_genre),
        len(titles_by_country),
    )
    return PreprocessingResult(
        df=step2,
        titles_by_genre=titles_by_genre,
        titles_by_country=titles_by_country,
        negative_lag_count=negative_lag_count,
    )


def save_processed_data(
    result: PreprocessingResult,
    processed_parquet: Path | None = None,
    processed_csv: Path | None = None,
    genre_parquet: Path | None = None,
    country_parquet: Path | None = None,
) -> dict[str, Path]:
    """Save the main processed dataset and exploded tables to ``data/processed/``.

    Args:
        result: :class:`PreprocessingResult` from :func:`preprocess_netflix_data`.
        processed_parquet: Optional override path for main Parquet file.
        processed_csv: Optional override path for main CSV file.
        genre_parquet: Optional override path for ``titles_by_genre.parquet``.
        country_parquet: Optional override path for ``titles_by_country.parquet``.

    Returns:
        Dictionary mapping output artifact names to their saved Paths.
    """
    pq_path = processed_parquet or PROCESSED_DATA_PARQUET
    csv_path = processed_csv or PROCESSED_DATA_CSV
    g_path = genre_parquet or TITLES_BY_GENRE_PARQUET
    c_path = country_parquet or TITLES_BY_COUNTRY_PARQUET

    for path in (pq_path, csv_path, g_path, c_path):
        path.parent.mkdir(parents=True, exist_ok=True)

    result.df.to_parquet(pq_path, index=False)
    result.df.to_csv(csv_path, index=False)
    result.titles_by_genre.to_parquet(g_path, index=False)
    result.titles_by_country.to_parquet(c_path, index=False)

    logger.info("Saved processed outputs to %s", pq_path.parent)
    return {
        "processed_parquet": pq_path,
        "processed_csv": csv_path,
        "titles_by_genre": g_path,
        "titles_by_country": c_path,
    }
