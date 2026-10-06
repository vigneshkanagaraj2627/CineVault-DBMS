# 🎬 CineVault — Movie Recommendation System (Desktop Application)

**College DBMS Mini Project — Backend + Database Integrated, Frontend/Backend Reorganized**

A dark-themed, Netflix/IMDb-inspired **desktop application** built with
**Python + CustomTkinter + Pillow**, fully backed by a real
**MongoDB Community Server** database via **PyMongo**. No Flask,
Django, HTML, CSS, or JavaScript is used anywhere — this is a native
desktop app. The project is organized into clear `frontend/` (GUI),
`backend/` (application + database logic), `dataset/`, and `scripts/`
folders.

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| GUI | Python, CustomTkinter, Tkinter, Pillow |
| Backend logic | Python (MVC-style controllers) |
| Database | MongoDB Community Server, PyMongo |
| Auth | bcrypt password hashing |

---

## ▶️ Quick Start

### 1. Install dependencies
```bash
cd cinevault
pip install -r requirements.txt
```

### 2. Make sure MongoDB is running
Start MongoDB Community Server locally (default port `27017`). You can
verify it's running by opening **MongoDB Compass** and connecting to:
```
mongodb://localhost:27017/
```
Confirm your existing `movie_recommendation_db.movies` collection
(with your ~1500 imported movies) is visible there.

### 3. Initialize the database (indexes + default admin)
```bash
python scripts/init_database.py
```
This is **safe to re-run** — it never touches your existing movie
documents, only adds indexes and (if none exists yet) creates one
default admin account.

### 4. Run CineVault
```bash
python main.py
```

---

## 🔑 Default Admin Login

The init script creates this admin account **only if no admin exists
yet**:

```
Email:    admin@cinevault.com
Password: Admin@123
```

⚠️ Please change this password after your first login (Settings →
Change Password), or edit `DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD`
at the top of `scripts/init_database.py` before running it.

Regular users register their own accounts from the Registration screen.

---

## 📁 Project Structure

```
cinevault/
├── main.py                            # App entry point (run this)
├── config.py                          # Theme colors, fonts, window settings
├── requirements.txt
├── README.md
│
├── frontend/                          # ★ Everything GUI-related
│   ├── views/                         # All 16 screens
│   │   ├── splash_screen.py
│   │   ├── login_window.py            # real email/password auth
│   │   ├── register_window.py         # real signup (bcrypt-hashed)
│   │   ├── dashboard_window.py        # real movies + "Recommended For You" shelf
│   │   ├── movie_details_window.py    # full real fields + live watchlist toggle
│   │   ├── search_window.py           # case-insensitive MongoDB search
│   │   ├── genre_filter_window.py     # dynamic genre chips from the real dataset
│   │   ├── rating_filter_window.py    # 0-10 IMDb-style rating buckets
│   │   ├── watchlist_window.py        # persists in the user's MongoDB document
│   │   ├── profile_window.py          # real name/email, editable + saved
│   │   ├── settings_window.py         # real password change (bcrypt)
│   │   ├── about_window.py
│   │   ├── admin_dashboard_window.py  # live stats + real catalog + quick delete
│   │   ├── add_movie_window.py        # real MongoDB insert, validated
│   │   ├── update_movie_window.py     # real MongoDB update, validated
│   │   ├── delete_movie_window.py     # real MongoDB delete, confirmation required
│   │   └── __init__.py
│   │
│   ├── widgets/                       # Reusable UI components
│   │   ├── movie_card.py
│   │   ├── sidebar.py
│   │   ├── rating_stars.py            # handles 0-10 IMDb-style ratings
│   │   ├── custom_widgets.py
│   │   ├── dialogs.py                 # themed error/success/confirm popups
│   │   └── __init__.py
│   │
│   └── assets/
│       ├── images/                    # reserved; this dataset has no poster URLs
│       └── fonts/
│
├── backend/                           # ★ Everything application/database logic
│   ├── controllers/                   # Real MongoDB-backed business logic
│   │   ├── auth_controller.py         # register/login, bcrypt hashing, dup-email check
│   │   ├── movie_controller.py        # search, filters, CRUD, genre parsing, stats
│   │   ├── user_controller.py         # watchlist, profile, password change
│   │   ├── recommendation_controller.py  # simple genre-based recommender
│   │   └── __init__.py
│   │
│   ├── models/                        # Data classes matching the REAL schema
│   │   ├── movie_model.py             # name, year, movie_rated, run_length, genres,
│   │   │                              # release_date, rating, num_raters, num_reviews
│   │   ├── user_model.py              # name, email, password, role, watchlist, created_at
│   │   └── __init__.py
│   │
│   ├── database/
│   │   ├── connection.py              # MongoDB connection singleton + error handling
│   │   └── __init__.py
│   │
│   └── utils/
│       ├── image_loader.py            # Pillow-generated placeholder posters/avatars
│       ├── navigation.py              # NavigationController — swaps views smoothly
│       ├── nav_config.py              # shared sidebar nav-item definitions
│       └── __init__.py
│
├── dataset/                            # Reserved for raw movie CSV/dataset files
│   └── README.md                       # (the app reads from MongoDB, not this folder)
│
└── scripts/
    ├── init_database.py                # Indexes + default admin, safe to re-run
    └── __init__.py
```

### Import convention after reorganization
Since `config.py` stays at the project root, every file still does
`from config import Colors, Fonts` regardless of how deep it lives —
this works because `main.py` (run from the root) puts the root
directory on Python's import path. All other internal imports now
follow the new package paths, e.g.:

```python
from frontend.views.dashboard_window import DashboardWindow
from frontend.widgets.movie_card import MovieCard
from backend.controllers.movie_controller import MovieController
from backend.models.movie_model import Movie
from backend.database.connection import get_db
from backend.utils.nav_config import build_nav_items
```

**Always run the app from the project root** (`python main.py`, not
from inside `frontend/` or `backend/`), so these imports resolve.

---

## 🗄️ Database Schema

### `movies` collection (your existing data — untouched)
```json
{
  "_id": ObjectId(...),
  "name": "Inception",
  "year": 2010,
  "movie_rated": "PG-13",
  "run_length": "2h 28min",
  "genres": "Action; Adventure; Sci-Fi;",
  "release_date": "16 July 2010 (USA)",
  "rating": 8.8,
  "num_raters": 1981675,
  "num_reviews": 3820
}
```

### `users` collection (created by `init_database.py`)
```json
{
  "_id": ObjectId(...),
  "name": "Arjun Kumar",
  "email": "arjun@example.com",
  "password": "$2b$12$...(bcrypt hash)...",
  "role": "user",
  "watchlist": [ObjectId("..."), ObjectId("...")],
  "created_at": ISODate("...")
}
```
`role` is either `"user"` or `"admin"`. A unique index on `email`
prevents duplicate accounts at the database level.

---

## 🧠 How Genre Parsing Works

Your dataset stores genres as a single semicolon-separated string:
```
"Action; Adventure; Sci-Fi;"
```
`models/movie_model.py::parse_genres()` splits this into a clean list
(`["Action", "Adventure", "Sci-Fi"]`) for display. For filtering,
`MovieController.filter_by_genre()` uses a MongoDB regex that matches
the genre as a **distinct segment** (bounded by `;` or string start/end),
so filtering by `"Action"` will never accidentally match a hypothetical
combined tag containing "Action" as a substring.

---

## 🎯 Recommendation System (for your viva)

`controllers/recommendation_controller.py` implements a simple,
fully explainable content-based approach:

1. Look at the genres of movies already in the user's watchlist.
2. Count how often each genre appears — this is the user's "genre profile."
3. Find movies rated ≥ 7.0 that share those genres and aren't already saved.
4. Rank by genre overlap first, then rating.
5. If the watchlist is empty, fall back to the overall top-rated movies.

One-sentence explanation for your viva: *"We recommend highly-rated
movies in the genres the user already likes, excluding what they've
already saved."*

---

## ✅ What Was Implemented This Phase

- Real MongoDB connection (`database/connection.py`) with friendly
  error dialogs if MongoDB isn't running
- Real bcrypt-hashed registration & login (no more dummy auth)
- Movies loaded live from your existing `movies` collection —
  dummy data removed entirely
- Case-insensitive search, genre filter, rating filter, year filter
  (combinable)
- Genre chips and rating buckets built dynamically / matched to the
  real 0-10 rating scale
- Per-user watchlist that persists in MongoDB across restarts
- Editable profile (name/email) and password change, both persisted
- Admin Dashboard with **live** stats (movie count, genre count,
  admin count, average rating) computed via MongoDB aggregation
- Full Add / Update / Delete Movie CRUD writing directly to MongoDB,
  with validation and confirmation dialogs
- Simple, explainable genre-based recommendation engine
- Themed error/success/confirm dialogs replacing all "dummy" print-only
  actions
- `scripts/init_database.py` for indexes + default admin (idempotent,
  non-destructive to your existing movies)

---

## 🧪 Verified

Because a live MongoDB server isn't available in the environment this
was built in, all backend logic (auth, search, genre parsing, filters,
watchlist, recommendations, CRUD, and `init_database.py`) was verified
against **mongomock** (an in-memory MongoDB simulator) with assertions
on every operation, and the full GUI was smoke-tested end-to-end
(all 16 screens, login → dashboard → details → watchlist → admin CRUD)
in a headless display. You should still do a final run against your
real MongoDB instance to confirm against your actual ~1500-movie
dataset before submission.
