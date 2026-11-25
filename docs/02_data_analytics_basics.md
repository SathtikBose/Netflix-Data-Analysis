# Data Analytics Basics (Plain-English Glossary)

New to data analytics? Don't worry! Here is every technical term used in this project, explained in plain English with everyday analogies.

---

## Core Data Terms

- **Dataset**: A structured collection of information—usually shaped like a giant spreadsheet. Our dataset is a spreadsheet of Netflix movies and TV shows.
- **Row (Record)**: One horizontal line in the spreadsheet. In our project, **1 row = 1 movie or TV show**.
- **Column (Field / Feature)**: One vertical category of information, such as `title`, `country`, or `release_year`.
- **CSV (Comma-Separated Values)**: A simple, universal text file for spreadsheets where columns are separated by commas.
- **Parquet**: A super-fast, compressed spreadsheet format built for data tools. It loads much faster than CSV and remembers whether a column is a date, a whole number, or text.
- **Null / Missing Value (`NaN` or `NA`)**: An empty cell where information is missing (for example, a TV show with no `director` listed).

---

## The Three Stages of Data Work

1. **Data Cleaning**:
   - *Analogy*: Washing vegetables and throwing away spoiled leaves before cooking.
   - Removing duplicates, trimming extra spaces, fixing values typed into the wrong column, and deciding how to handle empty cells (`nulls`).
2. **Data Preprocessing (Feature Engineering)**:
   - *Analogy*: Chopping and portioning ingredients so they are ready for the pan.
   - Creating useful new columns from existing ones—like splitting `"148 min"` into the number `148`, or subtracting `release_year` from `Year_Added` to see how old a movie was when Netflix added it.
3. **EDA (Exploratory Data Analysis)**:
   - *Analogy*: Tasting and looking at the dish as you ask questions—*Which country produces the most shows? Are TV shows growing faster than movies?*
   - Summarizing numbers and creating charts to spot patterns, trends, and surprises.

---

## Special Techniques Used in This Project

- **Deduplication**: Finding and removing accidental double-entries so the same movie isn't counted twice.
- **Imputation**: Filling in missing cells with a safe placeholder (we use `"Unknown"` for missing directors, cast, or countries) instead of deleting the whole row.
- **Explode**: Imagine a single cell says `"United States, United Kingdom"`. **Exploding** splits that one row into two rows—one for `"United States"` and one for `"United Kingdom"`—so both countries get fair credit when we count productions.
- **Outlier**: A data point that sits far outside the normal range (for example, a 300-minute movie when most movies are 90–120 minutes, or a negative lag where `Year_Added` is earlier than `release_year`).
- **Stacked Area Chart**: A chart showing how totals grow over time *and* how the parts (Movies vs. TV Shows) contribute to that total.
- **Heatmap**: A grid of colored squares where darker or brighter colors show bigger numbers—great for comparing **Countries × Genres** at a glance.
- **KPI (Key Performance Indicator)**: A single headline number (like *Total Titles* or *% TV Shows*) that gives you an instant health check.
