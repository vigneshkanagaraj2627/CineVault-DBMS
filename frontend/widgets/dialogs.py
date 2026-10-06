"""
widgets/dialogs.py
---------------------
Themed modal dialogs (error / success / info / confirm) so error
handling across the app looks consistent with the dark CineVault
theme instead of falling back to the plain OS-native tkinter
messagebox popups.

Usage:
    from frontend.widgets.dialogs import show_error, show_success, ask_confirm

    show_error(self, "Login Failed", "Incorrect password.")
    show_success(self, "Saved", "Movie added successfully.")
    if ask_confirm(self, "Delete Movie", "Are you sure?"):
        ...
"""

import customtkinter as ctk
from config import Colors, Fonts


class _BaseDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, icon="ℹ️", accent=Colors.PRIMARY):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x220")
        self.resizable(False, False)
        self.configure(fg_color=Colors.SURFACE)

        # Center relative to the parent window
        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw // 2) - 210
            y = py + (ph // 2) - 110
            self.geometry(f"420x220+{max(x, 0)}+{max(y, 0)}")
        except Exception:
            pass

        self.transient(parent)
        self.grab_set()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(container, text=icon, font=("Segoe UI", 32)).pack(pady=(0, 10))
        ctk.CTkLabel(container, text=title, font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY).pack(pady=(0, 8))
        ctk.CTkLabel(container, text=message, font=Fonts.BODY,
                     text_color=Colors.TEXT_SECONDARY, wraplength=360,
                     justify="center").pack(pady=(0, 18))

        self.button_row = ctk.CTkFrame(container, fg_color="transparent")
        self.button_row.pack()
        self._accent = accent

    def _ok_button(self, text="OK", command=None):
        ctk.CTkButton(
            self.button_row, text=text, width=140, height=38, corner_radius=8,
            fg_color=self._accent, hover_color=Colors.PRIMARY_HOVER,
            font=("Segoe UI", 13, "bold"),
            command=command or self.destroy
        ).pack(side="left", padx=6)


def show_error(parent, title="Error", message="Something went wrong."):
    dialog = _BaseDialog(parent, title, message, icon="⚠️", accent=Colors.ERROR)
    dialog._ok_button("OK")
    parent.wait_window(dialog)


def show_success(parent, title="Success", message="Done."):
    dialog = _BaseDialog(parent, title, message, icon="✅", accent=Colors.SUCCESS)
    dialog._ok_button("OK")
    parent.wait_window(dialog)


def show_info(parent, title="Info", message=""):
    dialog = _BaseDialog(parent, title, message, icon="ℹ️", accent=Colors.PRIMARY)
    dialog._ok_button("OK")
    parent.wait_window(dialog)


def ask_confirm(parent, title="Confirm", message="Are you sure?") -> bool:
    """Blocking confirmation dialog. Returns True if the user clicked
    Confirm, False if they clicked Cancel or closed the dialog."""
    dialog = _BaseDialog(parent, title, message, icon="❓", accent=Colors.ERROR)
    result = {"confirmed": False}

    def _confirm():
        result["confirmed"] = True
        dialog.destroy()

    ctk.CTkButton(
        dialog.button_row, text="Cancel", width=130, height=38, corner_radius=8,
        fg_color="transparent", border_width=1, border_color=Colors.BORDER,
        hover_color=Colors.SURFACE_LIGHT, text_color=Colors.TEXT_PRIMARY,
        font=("Segoe UI", 13, "bold"), command=dialog.destroy
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        dialog.button_row, text="Confirm", width=130, height=38, corner_radius=8,
        fg_color=Colors.ERROR, hover_color="#C0392B",
        font=("Segoe UI", 13, "bold"), command=_confirm
    ).pack(side="left", padx=6)

    parent.wait_window(dialog)
    return result["confirmed"]
