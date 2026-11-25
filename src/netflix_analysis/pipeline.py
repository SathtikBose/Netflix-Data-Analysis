"""Command-line pipeline orchestrator for Netflix Data Analysis.

Usage:
    python -m netflix_analysis.pipeline --stage clean
    python -m netflix_analysis.pipeline --stage all --prefer-sample
"""

from __future__ import annotations

import argparse

from netflix_analysis.cleaning import (
    clean_netflix_data,
    generate_data_quality_report,
    save_cleaned_data,
)
from netflix_analysis.config import setup_logging
from netflix_analysis.data_loader import load_netflix_data

logger = setup_logging()


def run_clean_stage(prefer_sample: bool = False) -> None:
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
    if args.stage in ("clean", "all"):
        run_clean_stage(prefer_sample=args.prefer_sample)
    if args.stage in ("preprocess", "eda", "all") and args.stage != "clean":
        logger.info("Stages 'preprocess' and 'eda' will be enabled in Phases 3 and 4.")


if __name__ == "__main__":
    main()
