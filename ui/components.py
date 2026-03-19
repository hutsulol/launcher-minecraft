"""Reusable UI components and theme constants for consistent styling."""

import tkinter as tk
from tkinter import ttk

# -- Color theme --
BG_DARK = "#1e1e2e"        # Main background
BG_CARD = "#2b2b3d"        # Card / panel background
BG_INPUT = "#3b3b4f"       # Entry field background
FG_PRIMARY = "#55ff55"     # Green accent (titles, success)
FG_TEXT = "#e0e0e0"        # Normal text
FG_MUTED = "#888899"       # Muted / secondary text
FG_ERROR = "#ff5555"       # Error text
BTN_GREEN = "#4CAF50"      # Primary button
BTN_GRAY = "#555566"       # Secondary button
BTN_RED = "#c0392b"        # Danger button

# -- Font presets --
FONT_TITLE = ("Arial", 22, "bold")
FONT_HEADING = ("Arial", 14, "bold")
FONT_BODY = ("Arial", 11)
FONT_SMALL = ("Arial", 9)
FONT_PLAY = ("Arial", 16, "bold")


def make_label(parent, text, font=FONT_BODY, fg=FG_TEXT, **kwargs):
    """Create a themed label."""
    return tk.Label(parent, text=text, font=font, fg=fg, bg=BG_DARK, **kwargs)


def make_entry(parent, width=28, show=None):
    """Create a themed entry field."""
    entry = tk.Entry(
        parent, width=width, show=show, font=FONT_BODY,
        bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
        relief="flat", highlightthickness=1,
        highlightbackground=BG_CARD, highlightcolor=FG_PRIMARY,
    )
    return entry


def make_button(parent, text, command, bg=BTN_GREEN, fg="white",
                width=22, font=FONT_BODY, **kwargs):
    """Create a themed button."""
    return tk.Button(
        parent, text=text, command=command, bg=bg, fg=fg,
        width=width, font=font, relief="flat", cursor="hand2",
        activebackground=bg, activeforeground=fg, **kwargs,
    )


def make_status_label(parent):
    """Create a status label for error/success messages."""
    return tk.Label(
        parent, text="", font=FONT_SMALL, fg=FG_MUTED,
        bg=BG_DARK, wraplength=300,
    )


def show_status(label, message, is_error=False):
    """Update a status label with a message."""
    color = FG_ERROR if is_error else FG_PRIMARY
    label.config(text=message, fg=color)


def make_separator(parent, width=300):
    """Create a horizontal separator line."""
    sep = tk.Frame(parent, bg=BG_CARD, height=1, width=width)
    return sep


def configure_combobox_style():
    """Apply dark theme to ttk Combobox widgets."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Dark.TCombobox",
        fieldbackground=BG_INPUT,
        background=BTN_GRAY,
        foreground=FG_TEXT,
        arrowcolor=FG_TEXT,
        selectbackground=BG_INPUT,
        selectforeground=FG_TEXT,
    )
