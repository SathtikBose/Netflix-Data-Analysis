"""Dataset loading and Kaggle download utilities.

Resolution order when loading the Netflix Movies and TV Shows dataset:
1. Local raw CSV at ``data/raw/netflix_titles.csv`` (if present).
2. Automatic download via the Kaggle API if credentials are configured
   (either via ``KAGGLE_USERNAME`` / ``KAGGLE_KEY`` environment variables
   or ``~/.kaggle/kaggle.json``).
3. Graceful fallback to the committed 300-row sample CSV at
   ``data/sample/netflix_titles_sample.csv``, accompanied by clear manual
   download instructions in the logs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd
from dotenv import load_dotenv

from netflix_analysis.config import (
    EXPECTED_COLUMNS,
    KAGGLE_DATASET_SLUG,
    RAW_DATASET_PATH,
    SAMPLE_DATASET_PATH,
    setup_logging,
)

logger = setup_logging()

DataSource = Literal["raw", "kaggle", "sample"]


@dataclass(frozen=True)
class LoadedDataset:
    """Container holding the loaded DataFrame and its provenance.

    Attributes:
        df: The loaded pandas DataFrame.
        source: Where the data came from (``"raw"``, ``"kaggle"``, or ``"sample"``).
        path: File path that was read.
    """

    df: pd.DataFrame
    source: DataSource
    path: Path


def has_kaggle_credentials() -> bool:
    """Check whether Kaggle API credentials are available locally.

    Loads variables from a ``.env`` file if present, then checks for either
    ``KAGGLE_USERNAME`` + ``KAGGLE_KEY`` environment variables or the standard
    ``~/.kaggle/kaggle.json`` file.

    Returns:
        ``True`` if credentials appear to be configured, ``False`` otherwise.
    """
    load_dotenv()
    has_env = bool(os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"))
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    return has_env or kaggle_json.is_file()


def download_from_kaggle(destination_dir: Path | None = None) -> Path:
    """Download and unzip the Netflix dataset from Kaggle.

    Args:
        destination_dir: Directory where ``netflix_titles.csv`` should be saved.
            Defaults to ``RAW_DATASET_PATH.parent``.

    Returns:
        Path to the downloaded ``netflix_titles.csv`` file.

    Raises:
        RuntimeError: If Kaggle credentials are missing or the download fails.
    """
    if not has_kaggle_credentials():
        raise RuntimeError(
            "Kaggle credentials not found. Set KAGGLE_USERNAME and KAGGLE_KEY "
            "in .env or place kaggle.json in ~/.kaggle/kaggle.json."
        )

    target_dir = destination_dir or RAW_DATASET_PATH.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        logger.info("Downloading '%s' from Kaggle into %s...", KAGGLE_DATASET_SLUG, target_dir)
        api.dataset_download_files(
            KAGGLE_DATASET_SLUG,
            path=str(target_dir),
            unzip=True,
        )
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to download dataset from Kaggle: {exc}") from exc

    downloaded_file = target_dir / RAW_DATASET_PATH.name
    if not downloaded_file.is_file():
        raise RuntimeError(
            f"Kaggle download completed, but expected file was not found at {downloaded_file}."
        )
    return downloaded_file


def log_manual_download_instructions(raw_path: Path) -> None:
    """Log beginner-friendly step-by-step instructions for manual download."""
    instructions = (
        "\n"
        "====================================================================\n"
        "Full Kaggle dataset not found locally. Using sample dataset instead.\n"
        "To use the full ~8,800-row dataset:\n"
        "  1. Visit https://www.kaggle.com/datasets/shivamb/netflix-shows\n"
        "  2. Click 'Download' (free Kaggle account required) and unzip.\n"
        f"  3. Place 'netflix_titles.csv' at:\n     {raw_path}\n"
        "  OR configure Kaggle API credentials (see docs/04_installation_and_setup.md).\n"
        "===================================================================="
    )
    logger.warning(instructions)


def validate_schema(df: pd.DataFrame, path: Path) -> None:
    """Verify that the loaded DataFrame contains all expected columns.

    Args:
        df: DataFrame to validate.
        path: Source file path (for clear error reporting).

    Raises:
        ValueError: If one or more expected columns are missing or DataFrame is empty.
    """
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset at {path} is missing expected columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )
    if df.empty:
        raise ValueError(f"Dataset at {path} is empty (0 rows).")


def load_netflix_data(
    raw_path: Path | None = None,
    sample_path: Path | None = None,
    allow_kaggle: bool = True,
    prefer_sample: bool = False,
) -> LoadedDataset:
    """Load the Netflix dataset from local raw file, Kaggle API, or sample fallback.

    Args:
        raw_path: Optional override path for the raw CSV.
        sample_path: Optional override path for the sample CSV.
        allow_kaggle: Whether to attempt a Kaggle API download if the raw file is missing.
        prefer_sample: If ``True``, skip raw/Kaggle and load the sample CSV directly.

    Returns:
        A :class:`LoadedDataset` containing the DataFrame, source label, and path.

    Raises:
        FileNotFoundError: If neither the raw dataset nor the sample dataset exists.
        ValueError: If the loaded CSV fails schema validation.
    """
    raw_target = raw_path or RAW_DATASET_PATH
    sample_target = sample_path or SAMPLE_DATASET_PATH

    if not prefer_sample:
        if raw_target.is_file():
            logger.info("Loading local raw dataset from %s", raw_target)
            df = pd.read_csv(raw_target)
            validate_schema(df, raw_target)
            return LoadedDataset(df=df, source="raw", path=raw_target)

        if allow_kaggle and has_kaggle_credentials():
            try:
                downloaded = download_from_kaggle(destination_dir=raw_target.parent)
                df = pd.read_csv(downloaded)
                validate_schema(df, downloaded)
                return LoadedDataset(df=df, source="kaggle", path=downloaded)
            except RuntimeError as exc:
                logger.warning("Kaggle download unsuccessful (%s). Falling back to sample.", exc)

        log_manual_download_instructions(raw_target)

    if not sample_target.is_file():
        raise FileNotFoundError(
            f"Sample dataset not found at {sample_target}. "
            "Please ensure data/sample/netflix_titles_sample.csv exists."
        )

    logger.info("Loading sample dataset from %s", sample_target)
    df = pd.read_csv(sample_target)
    validate_schema(df, sample_target)
    return LoadedDataset(df=df, source="sample", path=sample_target)


def main() -> None:
    """CLI entry point for ``python -m netflix_analysis.data_loader``."""
    result = load_netflix_data()
    logger.info(
        "Loaded %d rows and %d columns (source=%s, path=%s).",
        len(result.df),
        len(result.df.columns),
        result.source,
        result.path,
    )


if __name__ == "__main__":
    main()
