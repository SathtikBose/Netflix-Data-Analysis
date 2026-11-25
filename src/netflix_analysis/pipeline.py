"""Command-line pipeline orchestrator for Netflix Data Analysis.

Usage:
    python -m netflix_analysis.pipeline --stage clean
    python -m netflix_analysis.pipeline --stage preprocess
    python -m netflix_analysis.pipeline --stage all --prefer-sample
"""

from __future__ import annotations

import argparse

import pandas as pd

from netflix_analysis.cleaning import (
    clean_netflix_data,
    generate_data_quality_report,
    save_cleaned_data,
)
from netflix_analysis.config import CLEANED_DATA_PARQUET, setup_logging
from netflix_analysis.data_loader import load_netflix_data
from netflix_analysis.preprocessing import (
    PreprocessingResult,
    preprocess_netflix_data,
    save_processed_data,
)

logger = setup_logging()


def run_clean_stage(prefer_sample: bool = False) -> pd.DataFrame:
    """Execute data loading, cleaning, and quality report generation."""
    loaded = load_netflix_data(prefer_sample=prefer_sample)
    cleaning_result = clean_netflix_data(loaded.df)
    save_cleaned_data(cleaning_result.df)
    generate_data_quality_report(cleaning_result)
    logger.info(
        "Clean stage finished (%s source): %d -> %d rows.",
        loaded.source,
        cleaning_result.before.row_count,
        cleaning_result.after.row_count,
    )
    return cleaning_result.df


def run_preprocess_stage(cleaned_df: pd.DataFrame | None = None) -> PreprocessingResult:
    """Execute feature engineering and multi-label explosion."""
    if cleaned_df is None:
        if not CLEANED_DATA_PARQUET.is_file():
            raise FileNotFoundError(
                f"Cleaned dataset not found at {CLEANED_DATA_PARQUET}. "
                "Run '--stage clean' first."
            )
        logger.info("Loading cleaned dataset from %s", CLEANED_DATA_PARQUET)
        cleaned_df = pd.read_parquet(CLEANED_DATA_PARQUET)

    result = preprocess_netflix_data(cleaned_df)
    save_processed_data(result)
    logger.info("Preprocess stage finished: %d processed rows.", len(result.df))
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the pipeline."""
    parser = argparse.ArgumentParser(
        description="Run the Netflix Data Analysis pipeline.",
    )
    parser.add_argument(
        "--stage",
        choices=["clean", "preprocess", "eda", "all"],
        default="all",
        help="Which pipeline stage to run (default: all).",
    )
    parser.add_argument(
        "--prefer-sample",
        action="store_true",
        help="Use the committed 300-row sample dataset even if raw data exists.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for ``python -m netflix_analysis.pipeline``."""
    args = parse_args(argv)
    cleaned_df: pd.DataFrame | None = None

    if args.stage in ("clean", "all"):
        cleaned_df = run_clean_stage(prefer_sample=args.prefer_sample)

    if args.stage in ("preprocess", "all"):
        run_preprocess_stage(cleaned_df=cleaned_df)

    if args.stage in ("eda", "all"):
        logger.info("Stage 'eda' will be enabled in Phase 4.")


if __name__ == "__main__":
    main()
