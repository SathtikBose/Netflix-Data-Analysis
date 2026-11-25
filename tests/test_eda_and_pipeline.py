"""Unit tests for EDA functions and full-pipeline smoke test."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from netflix_analysis.cleaning import clean_netflix_data
from netflix_analysis.config import (
    CLEANED_DATA_PARQUET,
    DATA_QUALITY_REPORT_PATH,
    FIGURES_DIR,
    FINDINGS_REPORT_PATH,
    PROCESSED_DATA_PARQUET,
    TITLES_BY_COUNTRY_PARQUET,
    TITLES_BY_GENRE_PARQUET,
)
from netflix_analysis.data_loader import load_netflix_data
from netflix_analysis.eda import (
    plot_country_genre_heatmap,
    plot_growth_trajectory,
    plot_monthly_seasonality,
    plot_movie_duration_distribution,
    plot_ratings_by_decade,
    plot_top_countries,
    plot_top_description_terms,
    plot_top_directors_and_cast,
    run_eda_suite,
)
from netflix_analysis.pipeline import main as pipeline_main
from netflix_analysis.preprocessing import preprocess_netflix_data


def test_eda_chart_functions_return_figures_and_tables(tmp_path: Path) -> None:
    """Each EDA function should return a non-empty summary table, caption, and figure."""
    loaded = load_netflix_data(prefer_sample=True)
    cleaned = clean_netflix_data(loaded.df)
    prep = preprocess_netflix_data(cleaned.df)

    charts = [
        plot_growth_trajectory(prep.df),
        plot_top_countries(prep.titles_by_country),
        plot_country_genre_heatmap(prep.titles_by_country, prep.titles_by_genre),
        plot_ratings_by_decade(prep.df),
        plot_movie_duration_distribution(prep.df),
        plot_top_directors_and_cast(prep.df),
        plot_monthly_seasonality(prep.df),
        plot_top_description_terms(prep.df),
    ]

    for chart in charts:
        assert chart.figure is not None
        assert not chart.summary_table.empty
        assert len(chart.caption) > 10
        assert chart.filename.endswith(".png")
        plt.close(chart.figure)

    saved = run_eda_suite(
        df=prep.df,
        titles_by_genre=prep.titles_by_genre,
        titles_by_country=prep.titles_by_country,
        source="sample",
        figures_dir=tmp_path / "figures",
        findings_path=tmp_path / "findings.md",
    )
    assert len(saved) == 8
    assert all(p.is_file() for p in saved)
    findings_text = (tmp_path / "findings.md").read_text(encoding="utf-8")
    assert "Key Findings" in findings_text
    assert "296" in findings_text


def test_full_pipeline_smoke_test_on_sample() -> None:
    """Running '--stage all --prefer-sample' should produce all expected artifacts."""
    pipeline_main(["--stage", "all", "--prefer-sample"])

    assert CLEANED_DATA_PARQUET.is_file()
    assert PROCESSED_DATA_PARQUET.is_file()
    assert TITLES_BY_GENRE_PARQUET.is_file()
    assert TITLES_BY_COUNTRY_PARQUET.is_file()
    assert DATA_QUALITY_REPORT_PATH.is_file()
    assert FINDINGS_REPORT_PATH.is_file()

    pngs = list(FIGURES_DIR.glob("*.png"))
    assert len(pngs) == 8
