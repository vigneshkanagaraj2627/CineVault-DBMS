"""
scripts/import_movies.py
------------------------
Imports CineVault's cleaned movie dataset into MongoDB.

Input:
    dataset/movies_cleaned.csv

Target:
    movie_recommendation_db.movies

The script:
1. Reads the cleaned CSV using pandas.
2. Converts values to MongoDB-friendly Python types.
3. Converts genres and cast to arrays.
4. Replaces the old movies only after confirmation.
5. Imports the final movies.
6. Creates useful indexes.
7. Prints verification information.

The users collection is NOT deleted.
"""

import os
import sys

import pandas as pd
from pymongo import ASCENDING, DESCENDING


# ---------------------------------------------------------
# Allow imports from the CineVault project root
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from backend.database.connection import get_collection


# ---------------------------------------------------------
# Dataset path
# ---------------------------------------------------------

CSV_PATH = os.path.join(
    PROJECT_ROOT,
    "dataset",
    "movies_cleaned.csv"
)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def clean_text(value):
    """Convert a CSV value into clean text."""

    if pd.isna(value):
        return ""

    return str(value).strip()


def clean_int(value):
    """Convert numeric CSV values into int or None."""

    if pd.isna(value) or value == "":
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def clean_float(value):
    """Convert numeric CSV values into float or None."""

    if pd.isna(value) or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_list(value):
    """
    Convert genres/cast into a MongoDB array.

    Supports:
        Action, Drama, Thriller

    and:
        Action; Drama; Thriller
    """

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    if ";" in text:
        parts = text.split(";")
    else:
        parts = text.split(",")

    return [
        item.strip()
        for item in parts
        if item.strip()
    ]


# ---------------------------------------------------------
# Convert one CSV row to a MongoDB document
# ---------------------------------------------------------

def row_to_document(row):

    return {
        "title": clean_text(row.get("title")),

        "year": clean_int(row.get("year")),

        "certificate": clean_text(
            row.get("certificate")
        ),

        "duration": clean_int(
            row.get("duration")
        ),

        "genres": clean_list(
            row.get("genres")
        ),

        "rating": clean_float(
            row.get("rating")
        ),

        "metascore": clean_int(
            row.get("metascore")
        ),

        "director": clean_text(
            row.get("director")
        ),

        "cast": clean_list(
            row.get("cast")
        ),

        "votes": clean_int(
            row.get("votes")
        ),

        "description": clean_text(
            row.get("description")
        ),

        "review_count": clean_int(
            row.get("review_count")
        ),

        "review_title": clean_text(
            row.get("review_title")
        ),

        "review": clean_text(
            row.get("review")
        ),

        "poster_url": clean_text(
            row.get("poster_url")
        )
    }


# ---------------------------------------------------------
# Create indexes
# ---------------------------------------------------------

def create_indexes(collection):

    print("\nCreating MongoDB indexes...")

    collection.create_index(
        [("title", ASCENDING)]
    )

    collection.create_index(
        [("genres", ASCENDING)]
    )

    collection.create_index(
        [("rating", DESCENDING)]
    )

    collection.create_index(
        [("year", DESCENDING)]
    )

    collection.create_index(
        [
            ("rating", DESCENDING),
            ("votes", DESCENDING)
        ]
    )

    print("Indexes created successfully.")


# ---------------------------------------------------------
# Main import
# ---------------------------------------------------------

def import_movies():

    print("=" * 60)
    print("CineVault Final Movie Dataset Importer")
    print("=" * 60)

    # -----------------------------------------------------
    # Check dataset
    # -----------------------------------------------------

    if not os.path.exists(CSV_PATH):

        print("\nERROR:")
        print("movies_cleaned.csv was not found.")
        print("\nExpected location:")
        print(CSV_PATH)

        return

    print("\nDataset found:")
    print(CSV_PATH)

    # -----------------------------------------------------
    # Read CSV
    # -----------------------------------------------------

    print("\nReading cleaned dataset...")

    df = pd.read_csv(CSV_PATH)

    print(f"Movies found in CSV: {len(df)}")

    if df.empty:

        print("ERROR: Dataset is empty.")
        return

    # -----------------------------------------------------
    # Validate essential columns
    # -----------------------------------------------------

    required_columns = {
        "title",
        "genres",
        "rating"
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:

        print("\nERROR:")
        print(
            "Required columns are missing:"
        )

        for column in sorted(missing_columns):
            print(f"  - {column}")

        print("\nImport cancelled.")
        return

    # -----------------------------------------------------
    # Connect to MongoDB
    # -----------------------------------------------------

    print("\nConnecting to MongoDB...")

    try:
        movies_collection = get_collection(
            "movies"
        )

    except Exception as error:

        print("\nMongoDB connection failed:")
        print(error)
        return

    print("MongoDB connection successful.")

    # -----------------------------------------------------
    # Check existing movies
    # -----------------------------------------------------

    existing_count = (
        movies_collection.count_documents({})
    )

    print(
        f"\nExisting movies in MongoDB: "
        f"{existing_count}"
    )

    if existing_count > 0:

        print("\nWARNING")
        print(
            "The movies collection already contains data."
        )

        print(
            "Continuing will DELETE the old movies "
            "and replace them with the final dataset."
        )

        print(
            "\nThe users collection will NOT be deleted."
        )

        confirmation = input(
            '\nType REPLACE to continue: '
        ).strip()

        if confirmation != "REPLACE":

            print("\nImport cancelled.")
            print(
                "No existing movie data was changed."
            )

            return

    # -----------------------------------------------------
    # Prepare documents BEFORE deleting old movies
    # -----------------------------------------------------

    print("\nPreparing movie documents...")

    documents = []

    skipped = 0

    for _, row in df.iterrows():

        document = row_to_document(row)

        # Movie title is essential.
        if not document["title"]:

            skipped += 1
            continue

        documents.append(document)

    print(
        f"Documents prepared: {len(documents)}"
    )

    print(
        f"Documents skipped : {skipped}"
    )

    if not documents:

        print(
            "\nERROR: No valid movie documents "
            "were prepared."
        )

        print(
            "Existing MongoDB movies were NOT changed."
        )

        return

    # -----------------------------------------------------
    # Replace movies
    # -----------------------------------------------------

    if existing_count > 0:

        print("\nRemoving old movie documents...")

        delete_result = (
            movies_collection.delete_many({})
        )

        print(
            f"Old movies removed: "
            f"{delete_result.deleted_count}"
        )

    # -----------------------------------------------------
    # Insert final movies
    # -----------------------------------------------------

    print("\nImporting final movies...")

    try:

        result = movies_collection.insert_many(
            documents,
            ordered=False
        )

    except Exception as error:

        print("\nERROR DURING IMPORT:")
        print(error)

        print(
            "\nIMPORTANT: The old movies may already "
            "have been removed."
        )

        return

    imported_count = len(
        result.inserted_ids
    )

    print(
        f"Movies inserted: {imported_count}"
    )

    # -----------------------------------------------------
    # Indexes
    # -----------------------------------------------------

    create_indexes(
        movies_collection
    )

    # -----------------------------------------------------
    # Verify
    # -----------------------------------------------------

    final_count = (
        movies_collection.count_documents({})
    )

    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)

    print(
        f"CSV records       : {len(df)}"
    )

    print(
        f"Valid documents   : {len(documents)}"
    )

    print(
        f"Imported documents: {imported_count}"
    )

    print(
        f"MongoDB movies    : {final_count}"
    )

    # -----------------------------------------------------
    # Sample document
    # -----------------------------------------------------

    sample = movies_collection.find_one()

    if sample:

        print("\nSample imported movie:")

        print(
            f"Title   : {sample.get('title')}"
        )

        print(
            f"Year    : {sample.get('year')}"
        )

        print(
            f"Rating  : {sample.get('rating')}"
        )

        print(
            f"Genres  : {sample.get('genres')}"
        )

        print(
            f"Director: {sample.get('director')}"
        )

    print("\nThe users collection was not deleted.")

    print("=" * 60)


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":
    import_movies()