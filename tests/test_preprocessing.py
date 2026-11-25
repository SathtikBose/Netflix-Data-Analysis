"""Unit tests for the data preprocessing module."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from netflix_analysis.cleaning import clean_netflix_data
from netflix_analysis.data_loader import load_netflix_data
from netflix_analysis.preprocessing import (
    add_catalog_lag_features,
    build_exploded_table,
    preprocess_netflix_data,
    save_processed_data,
    split_duration_units,
    tokenize_csv_labels,
)


def _cleaned_sample_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "show_id": "s1",
                "type": "Movie",
                "title": "Movie One",
                "director": "Dir A",
                "cast": "Actor A",
                "country": "United States, United Kingdom",
                "date_added": pd.Timestamp("2021-06-15"),
                "release_year": 2020,
                "rating": "PG-13",
                "duration": "115 min",
                "listed_in": "Dramas, International Movies",
                "description": "Movie desc.",
            },
            {
                "show_id": "s2",
                "type": "TV Show",
                "title": "Show Two",
                "director": "Unknown",
                "cast": "Actor B",
                "country": "South Korea",
                "date_added": pd.Timestamp("2019-03-10"),
                "release_year": 2020,  # Negative lag (-1)
                "rating": "TV-MA",
                "duration": "2 Seasons",
                "listed_in": "Crime TV Shows, TV Dramas, Korean TV Shows",
                "description": "Show desc.",
            },
            {
                "show_id": "s3",
                "type": "Movie",
                "title": "Classic Film",
                "director": "Dir C",
                "cast": "Actor C",
                "country": "India",
                "date_added": pd.Timestamp("2020-01-05"),
                "release_year": 1995,  # Older licensed (+25)
                "rating": "TV-14",
                "duration": "140 min",
                "listed_in": "Comedies",
                "description": "Classic desc.",
            },
        ]
    )


def test_split_duration_units_separates_movies_and_tv_shows() -> None:
    """Movies populate Movie_Duration_Min; TV Shows populate TV_Seasons_Count."""
    df = _cleaned_sample_rows()
    out = split_duration_units(df)

    assert out.loc[0, "Movie_Duration_Min"] == 115
    assert pd.isna(out.loc[0, "TV_Seasons_Count"])
    assert pd.isna(out.loc[1, "Movie_Duration_Min"])
    assert out.loc[1, "TV_Seasons_Count"] == 2


def test_add_catalog_lag_features_handles_originals_licensed_and_negative_lag() -> None:
    """Lag math and Catalog_Category should classify 0-1, 2+, and <0 correctly."""
    df = _cleaned_sample_rows()
    out, neg_count = add_catalog_lag_features(df)

    assert neg_count == 1
    assert list(out["Year_Added"]) == [2021, 2019, 2020]
    assert list(out["Addition_Lag_Years"]) == [1, -1, 25]
    assert list(out["Catalog_Category"]) == [
        "New / Original (0-1 yr)",
        "Negative Lag (<0 yr)",
        "Older Licensed (2+ yrs)",
    ]
    assert list(out["Is_Original_Window"]) == [True, False, False]
    assert list(out["Audience_Group"]) == ["Teens", "Adults", "Teens"]


def test_tokenize_csv_labels_strips_and_handles_missing() -> None:
    """Comma-separated labels should be trimmed and missing values replaced."""
    series = pd.Series([" Dramas ,  Comedies ", pd.NA, " , "])
    tokens = tokenize_csv_labels(series)
    assert tokens.iloc[0] == ["Dramas", "Comedies"]
    assert tokens.iloc[1] == ["Unknown"]
    assert tokens.iloc[2] == ["Unknown"]


def test_build_exploded_table_credits_each_label() -> None:
    """Exploding genres and countries should produce exact expected row counts."""
    df = _cleaned_sample_rows()
    by_genre = build_exploded_table(df, source_col="listed_in", target_col="genre")
    by_country = build_exploded_table(df, source_col="country", target_col="country")

    # 2 + 3 + 1 = 6 genre rows; 2 + 1 + 1 = 4 country rows
    assert len(by_genre) == 6
    assert len(by_country) == 4
    assert "United Kingdom" in set(by_country["country"])
    assert "Korean TV Shows" in set(by_genre["genre"])


def test_preprocess_sample_dataset_and_save(tmp_path: Path) -> None:
    """End-to-end preprocessing on the cleaned 300-row sample should save all files."""
    loaded = load_netflix_data(prefer_sample=True)
    cleaned = clean_netflix_data(loaded.df)
    result = preprocess_netflix_data(cleaned.df)

    assert result.negative_lag_count >= 1
    assert len(result.df) == len(cleaned.df)
    assert len(result.titles_by_genre) >= len(result.df)
    assert len(result.titles_by_country) >= len(result.df)

    paths = save_processed_data(
        result,
        processed_parquet=tmp_path / "netflix_processed.parquet",
        processed_csv=tmp_path / "netflix_processed.csv",
        genre_parquet=tmp_path / "titles_by_genre.parquet",
        country_parquet=tmp_path / "titles_by_country.parquet",
    )
    assert all(path.is_file() for path in paths.values())
