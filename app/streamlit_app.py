"""Interactive Streamlit dashboard for the Netflix Movies & TV Shows analysis.

Designed for non-technical users:
- Automatically falls back to the 300-row sample dataset when the full
  Kaggle CSV is not present, displaying a clear banner.
- Caches data loading & preprocessing with ``@st.cache_data`` for fast filtering.
- Includes beginner-friendly "How to read this chart" expanders on every visual.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from netflix_analysis.cleaning import clean_netflix_data
from netflix_analysis.config import COLOR_PALETTE, UNKNOWN_PLACEHOLDER
from netflix_analysis.data_loader import load_netflix_data
from netflix_analysis.preprocessing import preprocess_netflix_data

st.set_page_config(
    page_title="Netflix Catalog Explorer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner="Loading and preparing Netflix catalog...")
def load_prepared_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    """Load, clean, and preprocess the dataset with caching."""
    loaded = load_netflix_data()
    cleaned = clean_netflix_data(loaded.df)
    prep = preprocess_netflix_data(cleaned.df)
    return prep.df, prep.titles_by_genre, prep.titles_by_country, loaded.source


def apply_filters(
    df: pd.DataFrame,
    by_genre: pd.DataFrame,
    by_country: pd.DataFrame,
    selected_types: list[str],
    year_range: tuple[int, int],
    selected_countries: list[str],
    selected_genres: list[str],
    selected_ratings: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Filter main and exploded DataFrames consistently by sidebar selections."""
    mask = (
        df["type"].isin(selected_types)
        & df["release_year"].between(year_range[0], year_range[1])
        & df["rating"].isin(selected_ratings)
    )
    filtered_ids = set(df.loc[mask, "show_id"])

    if selected_countries:
        country_ids = set(by_country.loc[by_country["country"].isin(selected_countries), "show_id"])
        filtered_ids &= country_ids

    if selected_genres:
        genre_ids = set(by_genre.loc[by_genre["genre"].isin(selected_genres), "show_id"])
        filtered_ids &= genre_ids

    f_df = df[df["show_id"].isin(filtered_ids)].copy()
    f_genre = by_genre[by_genre["show_id"].isin(filtered_ids)].copy()
    f_country = by_country[by_country["show_id"].isin(filtered_ids)].copy()

    if selected_countries:
        f_country = f_country[f_country["country"].isin(selected_countries)]
    if selected_genres:
        f_genre = f_genre[f_genre["genre"].isin(selected_genres)]

    return f_df, f_genre, f_country


def main() -> None:
    """Render the Streamlit dashboard."""
    df, by_genre, by_country, source = load_prepared_data()

    st.title("🎬 Netflix Movies & TV Shows — Catalog Explorer")
    st.caption(
        "An interactive, beginner-friendly dashboard exploring Netflix's global catalog "
        "by format, country, genre, and audience maturity."
    )

    if source == "sample":
        st.warning(
            "**Sample Mode Active**: You are viewing the built-in **300-row sample dataset** "
            "(`data/sample/netflix_titles_sample.csv`). To explore the full ~8,800-row catalog, "
            "place `netflix_titles.csv` from Kaggle into `data/raw/` and refresh.",
            icon="ℹ️",
        )

    # -----------------------------------------------------------------------
    # Sidebar Filters
    # -----------------------------------------------------------------------
    st.sidebar.header("Filter Catalog")

    all_types = sorted(df["type"].dropna().unique().tolist())
    selected_types = st.sidebar.multiselect(
        "Content Type",
        options=all_types,
        default=all_types,
    )

    min_year = int(df["release_year"].min())
    max_year = int(df["release_year"].max())
    year_range = st.sidebar.slider(
        "Release Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

    country_options = sorted(
        c for c in by_country["country"].dropna().unique().tolist() if c != UNKNOWN_PLACEHOLDER
    )
    selected_countries = st.sidebar.multiselect(
        "Country (leave empty for all)",
        options=country_options,
        default=[],
    )

    genre_options = sorted(
        g for g in by_genre["genre"].dropna().unique().tolist() if g != UNKNOWN_PLACEHOLDER
    )
    selected_genres = st.sidebar.multiselect(
        "Genre (leave empty for all)",
        options=genre_options,
        default=[],
    )

    rating_options = sorted(df["rating"].dropna().unique().tolist())
    selected_ratings = st.sidebar.multiselect(
        "Maturity Rating",
        options=rating_options,
        default=rating_options,
    )

    if not selected_types or not selected_ratings:
        st.info("Please select at least one Content Type and one Maturity Rating in the sidebar.")
        return

    f_df, f_genre, f_country = apply_filters(
        df=df,
        by_genre=by_genre,
        by_country=by_country,
        selected_types=selected_types,
        year_range=year_range,
        selected_countries=selected_countries,
        selected_genres=selected_genres,
        selected_ratings=selected_ratings,
    )

    if f_df.empty:
        st.warning("No titles match your current filter combination. Try broadening the sidebar filters.")
        return

    # -----------------------------------------------------------------------
    # Tabs
    # -----------------------------------------------------------------------
    tab_overview, tab_growth, tab_geo, tab_ratings, tab_explorer, tab_about = st.tabs(
        [
            "Overview",
            "Growth Over Time",
            "Countries and Genres",
            "Ratings",
            "Data Explorer",
            "About / How to read this",
        ]
    )

    # 1. Overview Tab
    with tab_overview:
        total_titles = len(f_df)
        movie_cnt = int((f_df["type"] == "Movie").sum())
        tv_cnt = int((f_df["type"] == "TV Show").sum())
        movie_pct = (movie_cnt / total_titles * 100) if total_titles else 0.0
        tv_pct = (tv_cnt / total_titles * 100) if total_titles else 0.0

        valid_countries = f_country[f_country["country"] != UNKNOWN_PLACEHOLDER]
        top_country = (
            valid_countries.groupby("country")["show_id"].nunique().idxmax()
            if not valid_countries.empty
            else "N/A"
        )

        movies_dur = f_df[f_df["type"] == "Movie"]["Movie_Duration_Min"].dropna()
        med_dur = f"{int(movies_dur.median())} min" if not movies_dur.empty else "N/A"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Filtered Titles", f"{total_titles:,}")
        col2.metric("Movies / TV Split", f"{movie_pct:.0f}% / {tv_pct:.0f}%")
        col3.metric("Top Country", str(top_country))
        col4.metric("Median Movie Runtime", med_dur)

        st.divider()
        cat_counts = (
            f_df["Catalog_Category"].value_counts().reset_index(name="count")
        )
        cat_counts.columns = ["Catalog Category", "Titles"]
        fig_cat = px.bar(
            cat_counts,
            x="Catalog Category",
            y="Titles",
            color="Catalog Category",
            color_discrete_sequence=[
                COLOR_PALETTE["movie"],
                COLOR_PALETTE["tv_show"],
                COLOR_PALETTE["accent"],
            ],
            title="New / Originals (0–1 yr lag) vs. Older Licensed Library (2+ yrs)",
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        with st.expander("How to read this chart"):
            st.write(
                "This chart compares how many titles were added to Netflix within 0–1 year of "
                "their release (typically Netflix Originals or new releases) versus older licensed "
                "films/shows added 2 or more years later."
            )

    # 2. Growth Over Time Tab
    with tab_growth:
        growth_df = (
            f_df.dropna(subset=["Year_Added"])
            .groupby(["Year_Added", "type"])
            .size()
            .reset_index(name="Titles Added")
            .sort_values("Year_Added")
        )
        fig_growth = px.area(
            growth_df,
            x="Year_Added",
            y="Titles Added",
            color="type",
            color_discrete_map={
                "Movie": COLOR_PALETTE["movie"],
                "TV Show": COLOR_PALETTE["tv_show"],
            },
            title="Titles Added to Netflix Per Year (Movies vs. TV Shows)",
        )
        st.plotly_chart(fig_growth, use_container_width=True)
        with st.expander("How to read this chart"):
            st.write(
                "Each colored band shows how many Movies (blue) or TV Shows (orange-red) were "
                "added in a given year. Because they are stacked, the top edge shows total additions."
            )

    # 3. Countries and Genres Tab
    with tab_geo:
        c_valid = f_country[f_country["country"] != UNKNOWN_PLACEHOLDER]
        top_c = (
            c_valid.groupby("country")["show_id"]
            .nunique()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="Titles")
        )
        fig_countries = px.bar(
            top_c.sort_values("Titles", ascending=True),
            x="Titles",
            y="country",
            orientation="h",
            color_discrete_sequence=[COLOR_PALETTE["movie"]],
            title="Top 10 Content-Producing Countries",
        )
        st.plotly_chart(fig_countries, use_container_width=True)
        with st.expander("How to read this chart"):
            st.write(
                "Longer bars mean more titles produced in that country. Co-productions (like "
                "'United States, United Kingdom') give credit to every participating country."
            )

        g_valid = f_genre[f_genre["genre"] != UNKNOWN_PLACEHOLDER]
        merged = (
            c_valid[["show_id", "country"]]
            .drop_duplicates()
            .merge(g_valid[["show_id", "genre"]].drop_duplicates(), on="show_id")
        )
        chosen_c = top_c["country"].head(8).tolist()
        chosen_g = (
            g_valid.groupby("genre")["show_id"]
            .nunique()
            .sort_values(ascending=False)
            .head(8)
            .index.tolist()
        )
        heat = (
            merged[merged["country"].isin(chosen_c) & merged["genre"].isin(chosen_g)]
            .groupby(["country", "genre"])["show_id"]
            .nunique()
            .unstack(fill_value=0)
            .reindex(index=chosen_c, columns=chosen_g, fill_value=0)
        )
        if not heat.empty:
            fig_heat = px.imshow(
                heat,
                text_auto=True,
                color_continuous_scale="YlGnBu",
                title="Genre Dominance Across Top Countries",
                aspect="auto",
            )
            st.plotly_chart(fig_heat, use_container_width=True)
            with st.expander("How to read this chart"):
                st.write(
                    "Each square shows how many titles match a specific Country (row) and Genre "
                    "(column). Darker blue squares indicate stronger regional specialties."
                )

    # 4. Ratings Tab
    with tab_ratings:
        decade_grp = (
            f_df.groupby(["Release_Decade", "Audience_Group"])
            .size()
            .reset_index(name="Count")
        )
        decade_totals = decade_grp.groupby("Release_Decade")["Count"].transform("sum")
        decade_grp["Share (%)"] = (decade_grp["Count"] / decade_totals * 100).round(1)

        fig_ratings = px.bar(
            decade_grp,
            x="Release_Decade",
            y="Share (%)",
            color="Audience_Group",
            title="Audience Maturity Share Across Release Decades",
            color_discrete_sequence=[
                COLOR_PALETTE["movie"],
                COLOR_PALETTE["tv_show"],
                COLOR_PALETTE["accent"],
                COLOR_PALETTE["highlight"],
                COLOR_PALETTE["purple"],
            ],
        )
        st.plotly_chart(fig_ratings, use_container_width=True)
        with st.expander("How to read this chart"):
            st.write(
                "Each bar adds up to 100% for a release decade. Compare the height of the colored "
                "segments to see whether newer decades lean more toward Adults (TV-MA/R) or Kids/Family."
            )

    # 5. Data Explorer Tab
    with tab_explorer:
        search_query = st.text_input("Search by title, director, cast, or description", "")
        display_df = f_df
        if search_query.strip():
            q = search_query.strip().lower()
            text_cols = ["title", "director", "cast", "description"]
            match_mask = pd.Series(False, index=display_df.index)
            for col in text_cols:
                match_mask |= display_df[col].astype(str).str.lower().str.contains(q, na=False)
            display_df = display_df[match_mask]

        cols_to_show = [
            "show_id", "type", "title", "director", "country",
            "release_year", "Year_Added", "rating", "duration", "listed_in",
        ]
        st.dataframe(display_df[cols_to_show], use_container_width=True, hide_index=True)

        csv_bytes = display_df[cols_to_show].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Results as CSV",
            data=csv_bytes,
            file_name="netflix_filtered_catalog.csv",
            mime="text/csv",
        )

    # 6. About / How to read this Tab
    with tab_about:
        st.subheader("About This Dashboard")
        st.markdown(
            """
            This dashboard explores the **Netflix Movies and TV Shows** catalog (`shivamb/netflix-shows`).

            - **What it measures**: Titles available in the Netflix catalog (up to September 2021),
              including format, release year, addition date, country, genres, and maturity rating.
            - **What it does NOT measure**: Viewership numbers, watch hours, or user ratings.
            - **Co-productions & Multi-genre titles**: Countries and genres are *exploded* so every
              participating country and genre receives fair credit.
            - **Need help?** Check the `docs/` folder in the repository—starting with
              `docs/00_START_HERE.md`.
            """
        )


if __name__ == "__main__":
    main()
