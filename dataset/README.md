# dataset/

This folder is reserved for the raw movie dataset file(s) (e.g. CSV)
used to originally populate the `movies` collection in
`movie_recommendation_db`.

No CSV files were included in this reorganization since your dataset
was already imported into MongoDB directly. If you have the original
CSV(s) you used for that import, place them here for reference /
reproducibility — the application itself does NOT read from this
folder at runtime; it reads exclusively from MongoDB via
`backend/database/connection.py`.
