"""
navigation.py
--------------
A tiny, reusable navigation controller shared by the whole app.

Instead of every window creating its own Toplevel and managing
teardown manually, all views live as full-size CTkFrames inside a
single root window's "container". Navigating just swaps which
frame is currently packed/raised — this gives smooth, flicker-free
transitions and keeps a consistent window size/position.
"""


class NavigationController:
    """
    Holds a reference to the root app window and knows how to
    show a given view class inside the shared container.

    Usage inside any view:
        self.controller.show_view(DashboardWindow, user=self.user)
    """

    def __init__(self, root_app):
        self.root_app = root_app  # the CineVaultApp instance (has .container)
        self.history = []         # simple back-stack of (ViewClass, kwargs)

    def show_view(self, view_class, remember_history: bool = True, **kwargs):
        """Destroy current frame(s) in the container and mount a new view."""
        for child in self.root_app.container.winfo_children():
            child.destroy()

        if remember_history:
            self.history.append((view_class, kwargs))

        new_view = view_class(parent=self.root_app.container,
                               controller=self,
                               **kwargs)
        new_view.pack(fill="both", expand=True)
        return new_view

    def go_back(self):
        """Pop current view off history and show the previous one."""
        if len(self.history) > 1:
            self.history.pop()  # remove current
            prev_class, prev_kwargs = self.history[-1]
            self.show_view(prev_class, remember_history=False, **prev_kwargs)
        else:
            print("No previous screen in history.")
