"""Shared visualization styling and figure export helpers.

Uses a colorblind-safe Okabe-Ito inspired palette and consistent typography
so all exported PNG figures and notebook plots look cohesive and readable.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure

from netflix_analysis.config import COLOR_PALETTE, setup_logging

# Use non-interactive Agg backend when running in headless/CLI environments
if matplotlib.get_backend().lower() != "agg":
    matplotlib.use("Agg", force=False)

logger = setup_logging()

COLORBLIND_SEQUENCE: list[str] = [
    COLOR_PALETTE["movie"],      # Blue
    COLOR_PALETTE["tv_show"],    # Vermilion
    COLOR_PALETTE["accent"],     # Bluish Green
    COLOR_PALETTE["highlight"],  # Orange
    COLOR_PALETTE["purple"],     # Reddish Purple
    COLOR_PALETTE["neutral"],    # Sky Blue
    COLOR_PALETTE["muted"],      # Gray
]


def apply_chart_style() -> None:
    """Apply consistent, publication-friendly Matplotlib/Seaborn styling."""
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#CCCCCC",
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
            "legend.frameon": True,
            "legend.facecolor": "white",
            "legend.edgecolor": "#E0E0E0",
        }
    )


def add_caption(fig: Figure, caption: str) -> None:
    """Add a plain-English 'What this tells us' caption below the chart.

    Args:
        fig: Matplotlib Figure to annotate.
        caption: One-sentence plain-English takeaway.
    """
    fig.text(
        0.5,
        0.01,
        f"What this tells us: {caption}",
        ha="center",
        va="bottom",
        fontsize=9.5,
        style="italic",
        color="#333333",
        wrap=True,
    )


def save_figure(fig: Figure, output_path: Path, dpi: int = 150) -> Path:
    """Save a Matplotlib figure to disk and close it to free memory.

    Args:
        fig: Matplotlib Figure to save.
        output_path: Destination PNG path.
        dpi: Resolution in dots per inch.

    Returns:
        Path to the saved PNG file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    logger.info("Saved figure to %s", output_path)
    return output_path
