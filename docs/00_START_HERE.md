# Start Here: 5-Minute Overview

Welcome! If you have **zero background in data analytics or Python**, you are in the right place. This guide explains what this project is, what you get, and which document to read next.

---

## What Does This Project Do?

Think of Netflix's catalog like a giant, messy library where someone dumped thousands of index cards into a box—some cards are missing the author's name, some have the movie's runtime written in the age-rating box, and some movies are listed twice.

This project takes that messy catalog (**about 8,800 movies and TV shows**) and:
1. **Cleans it** — fixes typos, handles missing fields safely, and removes duplicates.
2. **Organizes it (Preprocesses it)** — splits multi-country and multi-genre labels so every country and genre gets fair credit, and calculates how long it took each title to reach Netflix.
3. **Explores it (EDA)** — turns the clean data into clear charts and plain-English insights.
4. **Shares it** — gives you an interactive web dashboard where anyone can filter and explore the catalog with zero code.

---

## What You Get

- **Interactive Dashboard** (`app/streamlit_app.py`) — point-and-click charts, filters, and searchable tables.
- **Automated Data Pipeline** (`src/netflix_analysis/`) — clean, tested Python code that turns raw CSV data into analysis-ready tables and PNG charts.
- **Step-by-Step Notebooks** (`notebooks/`) — interactive walkthroughs for learning.
- **Ready-to-Run Sample Data** (`data/sample/`) — a 300-row sample file so everything works immediately, even without a Kaggle account.
- **Plain-English Documentation** (`docs/`) — written for complete beginners.

---

## Recommended Reading Order

| Order | Document | What You'll Learn |
| :--- | :--- | :--- |
| **1** | [`01_what_is_this_project.md`](01_what_is_this_project.md) | The problem, dataset, and real-world questions answered (with an analogy). |
| **2** | [`02_data_analytics_basics.md`](02_data_analytics_basics.md) | Plain-English glossary of terms like *null*, *cleaning*, *explode*, and *EDA*. |
| **3** | [`03_dataset_guide.md`](03_dataset_guide.md) | Every column in the Netflix dataset explained, plus known data quirks. |
| **4** | [`04_installation_and_setup.md`](04_installation_and_setup.md) | Step-by-step setup on Windows, macOS, and Linux (including Kaggle API). |
| **5** | [`05_how_to_run.md`](05_how_to_run.md) | How to launch the dashboard, run the pipeline, or open the notebooks. |
| **6** | [`06_how_it_works.md`](06_how_it_works.md) | Visual architecture diagram and why each cleaning choice was made. |
| **7** | [`07_understanding_the_results.md`](07_understanding_the_results.md) | How to read every chart and important caveats to keep in mind. |
| **8** | [`08_deployment_guide.md`](08_deployment_guide.md) | How to publish your dashboard online for free. |
| **9** | [`09_testing_and_quality.md`](09_testing_and_quality.md) | How automated tests keep the project reliable. |
| **10** | [`10_troubleshooting_faq.md`](10_troubleshooting_faq.md) | Quick fixes for common errors and frequently asked questions. |
| **11** | [`11_customize_and_extend.md`](11_customize_and_extend.md) | Ideas and steps to make this project your own. |

> **Just want to see it running right now?** Jump straight to [`04_installation_and_setup.md`](04_installation_and_setup.md) and [`05_how_to_run.md`](05_how_to_run.md).
