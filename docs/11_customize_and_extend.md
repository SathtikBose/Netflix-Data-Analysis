# Customize and Extend This Project

Once you understand how the project works, making it your own is one of the best ways to learn and stand out in a portfolio!

---

## 1. Swap in a Newer or Different Dataset

1. Place a CSV with the same 12 columns at `data/raw/netflix_titles.csv` (or point `load_netflix_data(raw_path=...)` to your file).
2. If your dataset has different column names, update `EXPECTED_COLUMNS` in `src/netflix_analysis/config.py`.
3. Re-run `python -m netflix_analysis.pipeline --stage all` and `pytest` to verify everything still passes.

---

## 2. Add a New Chart to the Pipeline

1. Open `src/netflix_analysis/eda.py`.
2. Write a new function `plot_my_chart(df: pd.DataFrame) -> ChartResult` following the existing pattern:
   - Call `apply_chart_style()`
   - Build your Matplotlib figure with a clear title and labeled axes
   - Call `add_caption(fig, "One-sentence plain-English takeaway.")`
   - Return `ChartResult(figure=fig, summary_table=..., title=..., caption=..., filename="09_my_chart.png")`
3. Add your function to the `charts` list inside `run_eda_suite()`.

---

## 3. Add a New Filter to the Streamlit Dashboard

1. Open `app/streamlit_app.py`.
2. Add a new sidebar widget (e.g., `st.sidebar.multiselect("Catalog Category", ...)`).
3. Pass that selection into `apply_filters()` and filter `f_df["Catalog_Category"].isin(...)`.

---

## Ideas for Next Steps

- **Add a TV Seasons breakdown chart** using `TV_Seasons_Count` (how many shows end after 1 season vs. 3+ seasons?).
- **Compare Originals vs. Licensed growth** over time by plotting `Catalog_Category` by `Year_Added`.
- **Join external IMDb/TMDB ratings** (by title + release year) to compare catalog volume against audience ratings.
