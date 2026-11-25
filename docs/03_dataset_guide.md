# Dataset Guide: Inside `netflix_titles.csv`

This guide explains every column in the **Netflix Movies and TV Shows** dataset, shows real-looking examples, points out known quirks in the raw data, and explains where the data comes from.

---

## Dataset Overview

- **Dataset Name**: Netflix Movies and TV Shows
- **Source**: [Kaggle (`shivamb/netflix-shows`)](https://www.kaggle.com/datasets/shivamb/netflix-shows)
- **Curator / Attribution**: Curated by Shivam Bansal from Flixable's Netflix catalog listings.
- **Size**: ~8,807 rows (titles) and 12 columns in the full dataset (plus a 300-row sample in `data/sample/netflix_titles_sample.csv` for offline testing).
- **Time Span**: Covers titles added to Netflix up to **September 2021**.

> **Important Note**: This dataset describes **what was available in the Netflix catalog** (titles, genres, countries, ratings). It does **not** include viewership counts, watch hours, or revenue.

---

## Every Column Explained

| Column | What It Means (Plain English) | Example Value |
| :--- | :--- | :--- |
| `show_id` | A unique ID code assigned to each row. | `s1` |
| `type` | Whether the title is a **Movie** or a **TV Show**. | `Movie` |
| `title` | The name of the movie or TV show. | `Inception` |
| `director` | Who directed the title (often blank for TV shows). | `Christopher Nolan` |
| `cast` | Comma-separated list of main actors. | `Leonardo DiCaprio, Elliot Page` |
| `country` | Country or countries where the title was produced. | `United States, United Kingdom` |
| `date_added` | The date Netflix added the title to its catalog. | `September 9, 2021` |
| `release_year` | The year the movie or show originally came out. | `2010` |
| `rating` | Age/maturity rating (like PG-13 or TV-MA). | `TV-MA` |
| `duration` | Length in **minutes** (for Movies) or **seasons** (for TV Shows). | `148 min` or `2 Seasons` |
| `listed_in` | Comma-separated Netflix genres/categories. | `Dramas, International Movies` |
| `description` | Short plot summary shown on Netflix. | `A thief who steals corporate secrets...` |

---

## Known Quirks in the Raw Data

Real-world data is rarely spotless. Here are the exact quirks our cleaning pipeline fixes automatically:

1. **Missing metadata (`director`, `cast`, `country`)**:
   - Many TV shows do not list a single director, and some titles omit `cast` or `country`.
   - Instead of deleting thousands of valid titles, we fill these blanks with `"Unknown"`.
2. **A few rows missing `date_added` or `rating`**:
   - A tiny fraction of rows (~0.1–0.2%) have no `date_added` or `rating`. Since we need both for timeline and maturity charts, those few rows are dropped and logged.
3. **Leading/trailing spaces in `date_added`**:
   - Some dates look like `" September 9, 2021"` with an extra space at the front. We strip whitespace before converting text into real calendar dates.
4. **Misplaced durations inside `rating`**:
   - In a few famous rows (e.g., `"74 min"`, `"84 min"`), someone accidentally typed the movie's runtime into the `rating` box and left `duration` blank! Our cleaner detects this, moves `"74 min"` back into `duration`, and sets `rating` to `"Unknown"`.
5. **Multi-value cells (`country` and `listed_in`)**:
   - A co-production like `"United States, United Kingdom"` or a multi-genre film like `"Dramas, International Movies"` packs multiple labels into one cell. During preprocessing, we **explode** (split) these so every country and genre gets fair credit.
6. **Negative catalog lag**:
   - Occasionally `Year_Added` is 1 year *earlier* than `release_year` (e.g., a show listed with `release_year = 2020` added in late `2019` due to season/release-date updates). We keep and flag this explicitly rather than hiding it.
7. **Regional re-releases / duplicate titles**:
   - A small number of titles appear twice with the exact same `title`, `release_year`, and `director`. We detect and remove those duplicates so they are not counted twice.

---

## License & Usage

- **Code in this repository**: MIT License (see [`LICENSE`](../LICENSE)).
- **Kaggle Dataset**: Please follow Kaggle's dataset license and terms of service on [the dataset page](https://www.kaggle.com/datasets/shivamb/netflix-shows). Do **not** commit `data/raw/netflix_titles.csv` to a public GitHub repo—`.gitignore` already protects it for you.
