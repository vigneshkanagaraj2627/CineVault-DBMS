"""
scripts/clean_dataset.py
------------------------
Cleans the final CineVault IMDb dataset and creates a new CSV
that is easier to import into MongoDB.

Original file:
    dataset/imdb movie recommendation.csv

Output file:
    dataset/movies_cleaned.csv
"""

from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "dataset" / "imdb movie recommendation.csv"
OUTPUT_FILE = BASE_DIR / "dataset" / "movies_cleaned.csv"


# ---------------------------------------------------------
# CLEANING FUNCTION
# ---------------------------------------------------------

def clean_dataset():

    print("=" * 60)
    print("CineVault Dataset Cleaner")
    print("=" * 60)

    # Check whether dataset exists
    if not INPUT_FILE.exists():
        print("\nERROR: Dataset file not found!")
        print(f"Expected location:\n{INPUT_FILE}")
        return

    print("\nLoading dataset...")

    df = pd.read_csv(INPUT_FILE)

    original_count = len(df)

    print(f"Original movies: {original_count}")
    print(f"Original columns: {len(df.columns)}")

    # -----------------------------------------------------
    # 1. RENAME COLUMNS
    # -----------------------------------------------------

    column_mapping = {
        "Poster": "poster_url",
        "Title": "title",
        "Year": "year",
        "Certificate": "certificate",
        "Duration (min)": "duration",
        "Genre": "genres",
        "Rating": "rating",
        "Metascore": "metascore",
        "Director": "director",
        "Cast": "cast",
        "Votes": "votes",
        "Description": "description",
        "Review Count": "review_count",
        "Review Title": "review_title",
        "Review": "review"
    }

    df = df.rename(columns=column_mapping)

    print("\nColumns renamed successfully.")

    # -----------------------------------------------------
    # 2. REMOVE MOVIES WITHOUT A VALID TITLE
    # -----------------------------------------------------

    df["title"] = df["title"].astype("string").str.strip()

    df = df[
        df["title"].notna()
        & (df["title"] != "")
        & (df["title"].str.lower() != "nan")
    ]

    # -----------------------------------------------------
    # 3. CLEAN NUMERIC COLUMNS
    # -----------------------------------------------------

    numeric_columns = [
        "year",
        "duration",
        "rating",
        "metascore",
        "votes",
        "review_count"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Nullable integer fields
    df["year"] = df["year"].round().astype("Int64")
    df["duration"] = df["duration"].round().astype("Int64")
    df["metascore"] = df["metascore"].round().astype("Int64")
    df["votes"] = df["votes"].round().astype("Int64")
    df["review_count"] = df["review_count"].round().astype("Int64")

    # Rating remains decimal
    df["rating"] = df["rating"].round(1)

    # -----------------------------------------------------
    # 4. CLEAN TEXT COLUMNS
    # -----------------------------------------------------

    text_columns = [
        "poster_url",
        "certificate",
        "director",
        "description",
        "review_title",
        "review"
    ]

    for column in text_columns:

        df[column] = df[column].astype("string").str.strip()

        # Missing values become empty strings
        df[column] = df[column].fillna("")

    # -----------------------------------------------------
    # 5. CLEAN GENRES
    # -----------------------------------------------------

    # Store genres in a consistent comma-separated format.
    # The MongoDB import script can later convert this
    # into a real Python/MongoDB list.

    def clean_genres(value):

        if pd.isna(value):
            return ""

        genres = [
            genre.strip()
            for genre in str(value).split(",")
            if genre.strip()
        ]

        # Remove duplicates while keeping original order
        genres = list(dict.fromkeys(genres))

        return ", ".join(genres)

    df["genres"] = df["genres"].apply(clean_genres)

    # -----------------------------------------------------
    # 6. CLEAN CAST
    # -----------------------------------------------------

    def clean_cast(value):

        if pd.isna(value):
            return ""

        cast_members = [
            actor.strip()
            for actor in str(value).split(",")
            if actor.strip()
        ]

        cast_members = list(dict.fromkeys(cast_members))

        return ", ".join(cast_members)

    df["cast"] = df["cast"].apply(clean_cast)

    # -----------------------------------------------------
    # 7. REMOVE EXACT DUPLICATES
    # -----------------------------------------------------

    before_duplicates = len(df)

    df = df.drop_duplicates()

    removed_duplicates = before_duplicates - len(df)

    # -----------------------------------------------------
    # 8. REMOVE DUPLICATE MOVIE RECORDS
    # -----------------------------------------------------
    #
    # Same title + same year is treated as the same movie.
    #
    # We DO NOT remove movies merely because their titles
    # are the same, because remakes can share titles.

    before_movie_duplicates = len(df)

    df = df.drop_duplicates(
        subset=["title", "year"],
        keep="first"
    )

    removed_movie_duplicates = (
        before_movie_duplicates - len(df)
    )

    # -----------------------------------------------------
    # 9. VALIDATE RATINGS
    # -----------------------------------------------------

    # IMDb ratings should be between 0 and 10.
    # Invalid values become missing instead of deleting
    # the entire movie.

    df.loc[
        (df["rating"] < 0) | (df["rating"] > 10),
        "rating"
    ] = pd.NA

    # -----------------------------------------------------
    # 10. VALIDATE YEARS
    # -----------------------------------------------------

    # Keep reasonable movie years.
    # Invalid values become missing.

    df.loc[
        (df["year"] < 1888) | (df["year"] > 2035),
        "year"
    ] = pd.NA

    # -----------------------------------------------------
    # 11. RESET INDEX
    # -----------------------------------------------------

    df = df.reset_index(drop=True)

    # -----------------------------------------------------
    # 12. FINAL COLUMN ORDER
    # -----------------------------------------------------

    final_columns = [
        "title",
        "year",
        "certificate",
        "duration",
        "genres",
        "rating",
        "metascore",
        "director",
        "cast",
        "votes",
        "description",
        "review_count",
        "review_title",
        "review",
        "poster_url"
    ]

    df = df[final_columns]

    # -----------------------------------------------------
    # 13. SAVE CLEAN DATASET
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("CLEANING COMPLETE")
    print("=" * 60)

    print(f"\nOriginal records : {original_count}")
    print(f"Final records    : {len(df)}")

    print(
        f"Exact duplicates removed : "
        f"{removed_duplicates}"
    )

    print(
        f"Movie duplicates removed : "
        f"{removed_movie_duplicates}"
    )

    print("\nMissing values after cleaning:")

    important_columns = [
        "title",
        "year",
        "rating",
        "genres",
        "director",
        "poster_url"
    ]

    for column in important_columns:
        print(
            f"  {column:<15}: "
            f"{df[column].isna().sum()}"
        )

    print("\nCleaned dataset saved to:")
    print(OUTPUT_FILE)

    print("\nIMPORTANT:")
    print("The original CSV was NOT modified.")
    print("=" * 60)


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    clean_dataset()