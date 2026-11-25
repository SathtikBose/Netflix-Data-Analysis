"""Exploratory Data Analysis (EDA) functions, figure generation, and findings report.

Every plotting function returns a :class:`ChartResult` containing the Matplotlib
figure, the underlying summary DataFrame, a title, and a one-sentence
plain-English "What this tells us" caption. All numbers in ``reports/findings.md``
are computed directly from the processed data.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from netflix_analysis.config import (
    COLOR_PALETTE,
    FIGURES_DIR,
    FINDINGS_REPORT_PATH,
    UNKNOWN_PLACEHOLDER,
    setup_logging,
)
from netflix_analysis.viz import (
    COLORBLIND_SEQUENCE,
    add_caption,
    apply_chart_style,
    save_figure,
)

logger = setup_logging()

_STOPWORDS: frozenset[str] = frozenset(
    {
        "the", "and", "for", "with", "that", "this", "from", "into", "their", "they",
        "when", "while", "where", "which", "who", "whom", "whose", "what", "about",
        "after", "before", "between", "through", "during", "under", "over", "again",
        "his", "her", "hers", "she", "him", "you", "your", "are", "was", "were",
        "has", "have", "had", "been", "being", "will", "would", "can", "could",
        "should", "may", "might", "must", "not", "but", "out", "off", "all", "any",
        "one", "two", "new", "life", "young", "man", "woman", "family", "world",
        "find", "finds", "make", "makes", "take", "takes", "get", "gets", "set",
        "sample", "movie", "show", "entry", "testing", "offline", "exploration",
        "netflix", "catalog", "pipeline", "tv",
    }
)

_MONTH_ORDER: tuple[str, ...] = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


@dataclass(frozen=True)
class ChartResult:
    """Container returned by each EDA plotting function."""

    figure: Figure
    summary_table: pd.DataFrame
    title: str
    caption: str
    filename: str


def plot_growth_trajectory(df: pd.DataFrame) -> ChartResult:
    """Create a stacked area chart of titles added per year by type."""
    apply_chart_style()
    counts = (
        df.dropna(subset=["Year_Added"])
        .groupby(["Year_Added", "type"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    for col in ("Movie", "TV Show"):
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[["Movie", "TV Show"]]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.stackplot(
        counts.index.astype(int),
        counts["Movie"],
        counts["TV Show"],
        labels=["Movies", "TV Shows"],
        colors=[COLOR_PALETTE["movie"], COLOR_PALETTE["tv_show"]],
        alpha=0.85,
    )
    title = "Netflix Catalog Growth Over Time (Movies vs. TV Shows)"
    ax.set_title(title, pad=12)
    ax.set_xlabel("Year Added to Netflix")
    ax.set_ylabel("Number of Titles Added")
    ax.legend(loc="upper left")
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    peak_year = int(counts.sum(axis=1).idxmax())
    peak_total = int(counts.sum(axis=1).max())
    caption = (
        f"Catalog additions peaked in {peak_year} ({peak_total:,} titles), "
        "with TV Shows steadily expanding alongside Movies."
    )
    add_caption(fig, caption)
    return ChartResult(
        figure=fig,
        summary_table=counts.reset_index(),
        title=title,
        caption=caption,
        filename="01_growth_trajectory.png",
    )


def plot_top_countries(titles_by_country: pd.DataFrame, top_n: int = 10) -> ChartResult:
    """Create a horizontal bar chart of the top content-producing countries."""
    apply_chart_style()
    filtered = titles_by_country[titles_by_country["country"] != UNKNOWN_PLACEHOLDER]
    top_counts = (
        filtered.groupby("country")["show_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index(name="title_count")
    )

    fig, ax = plt.subplots(figsize=(10, 5.5))
    plot_df = top_counts.sort_values("title_count", ascending=True)
    ax.barh(plot_df["country"], plot_df["title_count"], color=COLOR_PALETTE["movie"], alpha=0.9)
    title = f"Top {len(top_counts)} Content-Producing Countries (Excluding Unknown)"
    ax.set_title(title, pad=12)
    ax.set_xlabel("Number of Titles (Co-Productions Credited to Each Country)")
    ax.set_ylabel("Country")
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    leader = top_counts.iloc[0]["country"] if not top_counts.empty else "N/A"
    leader_cnt = int(top_counts.iloc[0]["title_count"]) if not top_counts.empty else 0
    caption = (
        f"{leader} leads the catalog with {leader_cnt:,} titles, followed by major "
        "international hubs."
    )
    add_caption(fig, caption)
    return ChartResult(
        figure=fig,
        summary_table=top_counts,
        title=title,
        caption=caption,
        filename="02_top_countries.png",
    )


def plot_country_genre_heatmap(
    titles_by_country: pd.DataFrame,
    titles_by_genre: pd.DataFrame,
    top_countries: int = 8,
    top_genres: int = 8,
) -> ChartResult:
    """Create a heatmap of top countries vs. top genres."""
    apply_chart_style()
    c_df = titles_by_country[titles_by_country["country"] != UNKNOWN_PLACEHOLDER][
        ["show_id", "country"]
    ].drop_duplicates()
    g_df = titles_by_genre[titles_by_genre["genre"] != UNKNOWN_PLACEHOLDER][
        ["show_id", "genre"]
    ].drop_duplicates()

    merged = c_df.merge(g_df, on="show_id", how="inner")
    chosen_countries = (
        c_df.groupby("country")["show_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(top_countries)
        .index
    )
    chosen_genres = (
        g_df.groupby("genre")["show_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(top_genres)
        .index
    )

    matrix = (
        merged[merged["country"].isin(chosen_countries) & merged["genre"].isin(chosen_genres)]
        .groupby(["country", "genre"])["show_id"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(index=chosen_countries, columns=chosen_genres, fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(11, 6.2))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Number of Titles"},
    )
    title = f"Genre Dominance Across Top {len(chosen_countries)} Countries"
    ax.set_title(title, pad=12)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Country")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    caption = (
        "Darker cells highlight each country's signature genres, revealing clear regional "
        "specialties across the catalog."
    )
    add_caption(fig, caption)
    return ChartResult(
        figure=fig,
        summary_table=matrix.reset_index(),
        title=title,
        caption=caption,
        filename="03_country_genre_heatmap.png",
    )


def plot_ratings_by_decade(df: pd.DataFrame) -> ChartResult:
    """Create a 100% stacked bar chart of audience maturity groups by release decade."""
    apply_chart_style()
    group_order = ["Kids", "Older Kids / Family", "Teens", "Adults", "Unrated / Unknown"]
    counts = (
        df.groupby(["Release_Decade", "Audience_Group"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    for grp in group_order:
        if grp not in counts.columns:
            counts[grp] = 0
    counts = counts[group_order]
    pct = counts.div(counts.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 5.5))
    pct.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        color=COLORBLIND_SEQUENCE[: len(group_order)],
        width=0.72,
    )
    title = "Audience Maturity Profile Across Release Decades"
    ax.set_title(title, pad=12)
    ax.set_xlabel("Release Decade")
    ax.set_ylabel("Share of Titles (%)")
    ax.set_ylim(0, 100)
    plt.xticks(rotation=0)
    ax.legend(title="Audience Group", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    adult_latest = float(pct["Adults"].iloc[-1]) if not pct.empty else 0.0
    latest_decade = str(pct.index[-1]) if not pct.empty else "recent"
    caption = (
        f"In the {latest_decade}, Adult-rated content (TV-MA/R/NC-17) accounts for "
        f"{adult_latest:.1f}% of catalog releases."
    )
    add_caption(fig, caption)
    return ChartResult(
        figure=fig,
        summary_table=counts.reset_index(),
        title=title,
        caption=caption,
        filename="04_ratings_by_decade.png",
    )


def plot_movie_duration_distribution(df: pd.DataFrame) -> ChartResult:
    """[Extra] Histogram of movie runtimes in minutes."""
    apply_chart_style()
    movies = df[df["type"] == "Movie"].dropna(subset=["Movie_Duration_Min"])
    durations = movies["Movie_Duration_Min"].astype(int)

    fig, ax = plt.subplots(figsize=(10, 5.2))
    sns.histplot(durations, bins=25, kde=True, color=COLOR_PALETTE["movie"], ax=ax)
    median_val = float(durations.median()) if not durations.empty else 0.0
    ax.axvline(
        median_val,
        color=COLOR_PALETTE["tv_show"],
        linestyle="--",
        linewidth=2,
        label=f"Median: {median_val:.0f} min",
    )
    title = "[Extra] Distribution of Movie Runtimes"
    ax.set_title(title, pad=12)
    ax.set_xlabel("Duration (Minutes)")
    ax.set_ylabel("Number of Movies")
    ax.legend()
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    caption = (
        f"Most movies cluster around the median runtime of {median_val:.0f} minutes "
        "(roughly 1.5 to 2 hours)."
    )
    add_caption(fig, caption)
    summary = durations.describe().reset_index()
    summary.columns = ["metric", "value"]
    return ChartResult(
        figure=fig,
        summary_table=summary,
        title=title,
        caption=caption,
        filename="05_extra_movie_duration_dist.png",
    )


def plot_top_directors_and_cast(df: pd.DataFrame, top_n: int = 10) -> ChartResult:
    """[Extra] Side-by-side horizontal bars for top directors and top actors."""
    apply_chart_style()
    directors = (
        df[df["director"] != UNKNOWN_PLACEHOLDER]["director"]
        .str.split(",")
        .explode()
        .str.strip()
    )
    top_dirs = directors[directors != ""].value_counts().head(top_n).reset_index()
    top_dirs.columns = ["name", "count"]

    actors = (
        df[df["cast"] != UNKNOWN_PLACEHOLDER]["cast"]
        .str.split(",")
        .explode()
        .str.strip()
    )
    top_actors = actors[actors != ""].value_counts().head(top_n).reset_index()
    top_actors.columns = ["name", "count"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    d_plot = top_dirs.sort_values("count", ascending=True)
    ax1.barh(d_plot["name"], d_plot["count"], color=COLOR_PALETTE["movie"])
    ax1.set_title("Top Directors")
    ax1.set_xlabel("Title Count")

    a_plot = top_actors.sort_values("count", ascending=True)
    ax2.barh(a_plot["name"], a_plot["count"], color=COLOR_PALETTE["accent"])
    ax2.set_title("Top Cast Members")
    ax2.set_xlabel("Title Count")

    title = "[Extra] Most Frequent Directors & Cast Members (Excluding Unknown)"
    fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))

    top_dir_name = top_dirs.iloc[0]["name"] if not top_dirs.empty else "N/A"
    top_act_name = top_actors.iloc[0]["name"] if not top_actors.empty else "N/A"
    caption = (
        f"'{top_dir_name}' leads directors and '{top_act_name}' leads cast appearances "
        "in the analyzed catalog."
    )
    add_caption(fig, caption)

    combined = pd.concat(
        [top_dirs.assign(role="Director"), top_actors.assign(role="Actor")],
        ignore_index=True,
    )
    return ChartResult(
        figure=fig,
        summary_table=combined,
        title=title,
        caption=caption,
        filename="06_extra_top_directors_cast.png",
    )


def plot_monthly_seasonality(df: pd.DataFrame) -> ChartResult:
    """[Extra] Bar chart of catalog additions by calendar month."""
    apply_chart_style()
    counts = (
        df["Month_Added_Name"]
        .value_counts()
        .reindex(list(_MONTH_ORDER), fill_value=0)
        .reset_index()
    )
    counts.columns = ["month", "title_count"]

    fig, ax = plt.subplots(figsize=(10, 5.0))
    ax.bar(counts["month"], counts["title_count"], color=COLOR_PALETTE["highlight"], alpha=0.9)
    title = "[Extra] Monthly Seasonality of Netflix Catalog Additions"
    ax.set_title(title, pad=12)
    ax.set_xlabel("Month Added")
    ax.set_ylabel("Number of Titles Added")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    peak_row = counts.loc[counts["title_count"].idxmax()] if not counts.empty else None
    peak_month = str(peak_row["month"]) if peak_row is not None else "N/A"
    peak_val = int(peak_row["title_count"]) if peak_row is not None else 0
    caption = (
        f"Catalog additions peak in {peak_month} ({peak_val:,} titles), showing how "
        "release schedules vary across the year."
    )
    add_caption(fig, caption)
    return ChartResult(
        figure=fig,
        summary_table=counts,
        title=title,
        caption=caption,
        filename="07_extra_monthly_seasonality.png",
    )


def plot_top_description_terms(df: pd.DataFrame, top_n: int = 15) -> ChartResult:
    """[Extra] Horizontal bar chart of the most common meaningful words in descriptions."""
    apply_chart_style()
    counter: Counter[str] = Counter()
    for text in df["description"].dropna().astype(str):
        tokens = re.findall(r"[a-z]{3,}", text.lower())
        counter.update(tok for tok in tokens if tok not in _STOPWORDS)

    top_terms = pd.DataFrame(counter.most_common(top_n), columns=["term", "frequency"])
    if top_terms.empty:
        top_terms = pd.DataFrame([{"term": "none", "frequency": 0}])

    fig, ax = plt.subplots(figsize=(10, 5.5))
    plot_df = top_terms.sort_values("frequency", ascending=True)
    ax.barh(plot_df["term"], plot_df["frequency"], color=COLOR_PALETTE["purple"], alpha=0.9)
    title = "[Extra] Top Terms in Title Descriptions"
    ax.set_title(title, pad=12)
    ax.set_xlabel("Word Frequency")
    ax.set_ylabel("Term")
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    top_word = str(top_terms.iloc[0]["term"])
    caption = (
        f"Plot summaries frequently highlight themes around '{top_word}', reflecting "
        "common storytelling hooks across the catalog."
    )
    add_caption(fig, caption)
    return ChartResult(
        figure=fig,
        summary_table=top_terms,
        title=title,
        caption=caption,
        filename="08_extra_description_top_terms.png",
    )


def generate_findings_report(
    df: pd.DataFrame,
    titles_by_country: pd.DataFrame,
    titles_by_genre: pd.DataFrame,
    source: str = "sample",
    output_path: Path | None = None,
) -> Path:
    """Compute summary statistics from processed data and write ``reports/findings.md``."""
    target = output_path or FINDINGS_REPORT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    total_titles = len(df)
    movie_count = int((df["type"] == "Movie").sum())
    tv_count = int((df["type"] == "TV Show").sum())
    movie_pct = (movie_count / total_titles * 100) if total_titles else 0.0
    tv_pct = (tv_count / total_titles * 100) if total_titles else 0.0

    year_counts = df.groupby("Year_Added").size()
    peak_year = int(year_counts.idxmax()) if not year_counts.empty else 0
    peak_year_count = int(year_counts.max()) if not year_counts.empty else 0

    top_countries = (
        titles_by_country[titles_by_country["country"] != UNKNOWN_PLACEHOLDER]
        .groupby("country")["show_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(5)
    )
    top_genres = (
        titles_by_genre[titles_by_genre["genre"] != UNKNOWN_PLACEHOLDER]
        .groupby("genre")["show_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(5)
    )

    movies_dur = df[df["type"] == "Movie"]["Movie_Duration_Min"].dropna()
    avg_movie_min = float(movies_dur.mean()) if not movies_dur.empty else 0.0
    med_movie_min = float(movies_dur.median()) if not movies_dur.empty else 0.0

    originals_cnt = int((df["Catalog_Category"] == "New / Original (0-1 yr)").sum())
    licensed_cnt = int((df["Catalog_Category"] == "Older Licensed (2+ yrs)").sum())
    neg_lag_cnt = int((df["Catalog_Category"] == "Negative Lag (<0 yr)").sum())

    adult_cnt = int((df["Audience_Group"] == "Adults").sum())
    adult_pct = (adult_cnt / total_titles * 100) if total_titles else 0.0

    source_note = (
        "> **Note**: These figures were computed from the **300-row sample dataset** "
        "(`data/sample/netflix_titles_sample.csv`). Add the full Kaggle `netflix_titles.csv` "
        "to `data/raw/` and re-run `python -m netflix_analysis.pipeline --stage all` for full-catalog numbers."
        if source == "sample"
        else "> **Source**: Computed from the full local/Kaggle `netflix_titles.csv` dataset."
    )

    lines = [
        "# Key Findings: Netflix Movies & TV Shows",
        "",
        source_note,
        "",
        "## 1. Catalog Composition & Growth",
        "",
        f"- **Total Cleaned Titles**: **{total_titles:,}**",
        f"- **Movies vs. TV Shows**: **{movie_count:,}** Movies ({movie_pct:.1f}%) and **{tv_count:,}** TV Shows ({tv_pct:.1f}%).",
        f"- **Peak Addition Year**: **{peak_year}** with **{peak_year_count:,}** titles added.",
        "",
        "## 2. Production Hubs & Top Genres",
        "",
        "- **Top 5 Content-Producing Countries** (excluding `Unknown`):",
    ]
    for country, cnt in top_countries.items():
        lines.append(f"  - {country}: **{int(cnt):,}** titles")

    lines.append("- **Top 5 Genres** (exploded multi-label counts):")
    for genre, cnt in top_genres.items():
        lines.append(f"  - {genre}: **{int(cnt):,}** titles")

    lines.extend(
        [
            "",
            "## 3. Audience Maturity & Catalog Strategy",
            "",
            f"- **Adult-Oriented Programming** (`TV-MA`, `R`, `NC-17`): **{adult_cnt:,}** titles (**{adult_pct:.1f}%** of catalog).",
            f"- **New / Original Window (0–1 yr lag)**: **{originals_cnt:,}** titles.",
            f"- **Older Licensed Library (2+ yrs lag)**: **{licensed_cnt:,}** titles.",
            f"- **Negative Lag (<0 yr, preserved & flagged)**: **{neg_lag_cnt:,}** title(s).",
            "",
            "## 4. Extras: Runtime Snapshot",
            "",
            f"- **Movie Runtime**: Mean **{avg_movie_min:.1f} min**, Median **{med_movie_min:.0f} min**.",
            "",
        ]
    )

    target.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Saved key findings report to %s", target)
    return target


def run_eda_suite(
    df: pd.DataFrame,
    titles_by_genre: pd.DataFrame,
    titles_by_country: pd.DataFrame,
    source: str = "sample",
    figures_dir: Path | None = None,
    findings_path: Path | None = None,
) -> list[Path]:
    """Generate all EDA charts, save PNGs, and write ``reports/findings.md``."""
    fig_dir = figures_dir or FIGURES_DIR
    fig_dir.mkdir(parents=True, exist_ok=True)

    charts: list[ChartResult] = [
        plot_growth_trajectory(df),
        plot_top_countries(titles_by_country),
        plot_country_genre_heatmap(titles_by_country, titles_by_genre),
        plot_ratings_by_decade(df),
        plot_movie_duration_distribution(df),
        plot_top_directors_and_cast(df),
        plot_monthly_seasonality(df),
        plot_top_description_terms(df),
    ]

    saved_paths: list[Path] = []
    for chart in charts:
        saved_paths.append(save_figure(chart.figure, fig_dir / chart.filename))

    generate_findings_report(
        df=df,
        titles_by_country=titles_by_country,
        titles_by_genre=titles_by_genre,
        source=source,
        output_path=findings_path,
    )
    return saved_paths
