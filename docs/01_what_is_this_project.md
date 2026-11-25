# What Is This Project?

Imagine you walk into a huge video rental store with **8,800 DVDs** stacked in boxes. Someone asks you:
- *"Does this store carry more movies or TV shows?"*
- *"Which countries make the most titles here?"*
- *"Are most titles for kids, teens, or adults?"*

You couldn't answer by squinting at the boxes. First, you would **tidy up the labels** (cleaning), **sort them onto shelves by genre and country** (preprocessing), and **draw a map of what's on the shelves** (Exploratory Data Analysis, or **EDA**).

That is exactly what this project does for Netflix's catalog.

---

## The Problem We Solve

Raw real-world datasets are messy:
- Some rows are missing directors, actors, or countries.
- Dates have extra spaces, and a few movie runtimes were accidentally typed into the age-rating column.
- Multi-country co-productions (like `"United States, United Kingdom"`) are crammed into one cell.

This project provides a **clean, tested, automated pipeline** that turns that messy CSV into trustworthy charts, a written findings report, and an **interactive web dashboard** anyone can explore without writing code.

---

## Key Questions Answered

1. **Growth Trajectory**: How fast did Netflix's catalog grow, and did TV Shows catch up to Movies?
2. **Global Production Hubs**: Which countries produce the most Netflix titles, and what genres does each country specialize in?
3. **Audience Maturity**: Are newer releases shifting toward mature (`TV-MA`, `R`) ratings compared to older decades?
4. **Catalog Strategy & Extras**: How many titles are newly released Originals (0–1 year lag) vs. older licensed library films? What is the typical movie runtime, and which months see the most additions?

---

## Who This Helps

- **Beginners learning data analytics**: Every step is documented in plain English and paired with Jupyter notebooks.
- **Portfolio builders**: Shows production-grade engineering (modular Python, unit tests, linting, Docker, and a live Streamlit app).
- **Non-technical explorers**: Anyone can open the Streamlit dashboard and filter Netflix's catalog with point-and-click controls.
