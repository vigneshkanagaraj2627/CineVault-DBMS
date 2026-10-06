"""
utils/nav_config.py
----------------------
Single source of truth for the sidebar's navigation items. Every
view that shows a Sidebar calls build_nav_items(user) instead of
re-importing every view class and re-typing the same list, keeping
the codebase DRY and easy to maintain.
"""


def build_nav_items(user):
    """Returns the standard nav_items list used by Sidebar on every
    authenticated screen. Imports are local to avoid circular imports."""
    from frontend.views.dashboard_window import DashboardWindow
    from frontend.views.search_window import SearchWindow
    from frontend.views.genre_filter_window import GenreFilterWindow
    from frontend.views.rating_filter_window import RatingFilterWindow
    from frontend.views.watchlist_window import WatchlistWindow
    from frontend.views.profile_window import ProfileWindow
    from frontend.views.settings_window import SettingsWindow
    from frontend.views.about_window import AboutWindow

    return [
        ("Dashboard", "🏠", DashboardWindow, {"user": user}),
        ("Search", "🔍", SearchWindow, {"user": user}),
        ("Genres", "🎬", GenreFilterWindow, {"user": user}),
        ("Top Rated", "⭐", RatingFilterWindow, {"user": user}),
        ("Watchlist", "📌", WatchlistWindow, {"user": user}),
        ("Profile", "👤", ProfileWindow, {"user": user}),
        ("Settings", "⚙️", SettingsWindow, {"user": user}),
        ("About", "ℹ️", AboutWindow, {"user": user}),
    ]


def build_admin_nav_items(user):
    """Nav items for the Admin Dashboard section (separate sidebar set)."""
    from frontend.views.admin_dashboard_window import AdminDashboardWindow
    from frontend.views.add_movie_window import AddMovieWindow
    from frontend.views.update_movie_window import UpdateMovieWindow
    from frontend.views.delete_movie_window import DeleteMovieWindow
    from frontend.views.settings_window import SettingsWindow
    from frontend.views.about_window import AboutWindow

    return [
        ("Admin Home", "🏠", AdminDashboardWindow, {"user": user}),
        ("Add Movie", "➕", AddMovieWindow, {"user": user}),
        ("Update Movie", "✏️", UpdateMovieWindow, {"user": user}),
        ("Delete Movie", "🗑️", DeleteMovieWindow, {"user": user}),
        ("Settings", "⚙️", SettingsWindow, {"user": user}),
        ("About", "ℹ️", AboutWindow, {"user": user}),
    ]
