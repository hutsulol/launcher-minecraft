"""Pirate / Sea theme constants and Canvas drawing helpers for Lungi Launcher."""

import tkinter as tk

# ======================================================================
# Colors
# ======================================================================
BG_DEEP = "#020617"         # Deepest ocean (window bg)
BG_DARK = "#0f172a"         # Dark navy (panels, top bar)
BG_CARD = "#1e293b"         # Card background
BG_CARD_HOVER = "#334155"   # Card hover highlight
BG_INPUT = "#1e293b"        # Entry field background
BG_TOPBAR = "#0f172a"       # Top bar background

GOLD = "#facc15"            # Gold accent (titles, highlights)
GOLD_DIM = "#a38a0e"        # Dimmed gold
EMERALD = "#10b981"         # Play button green
EMERALD_HOVER = "#059669"   # Play button hover
FG_TEXT = "#e2e8f0"         # Light text
FG_MUTED = "#64748b"        # Muted / secondary text
FG_ERROR = "#ef4444"        # Error red
FG_SUCCESS = "#10b981"      # Success green

BTN_PRIMARY = "#10b981"     # Primary button (emerald)
BTN_SECONDARY = "#334155"   # Secondary button (slate)
BTN_DANGER = "#dc2626"      # Danger button

# ======================================================================
# Fonts
# ======================================================================
FONT_LOGO = ("Arial", 20, "bold")
FONT_TITLE = ("Arial", 26, "bold")
FONT_HEADING = ("Arial", 14, "bold")
FONT_BODY = ("Arial", 11)
FONT_SMALL = ("Arial", 9)
FONT_TINY = ("Arial", 8)
FONT_PLAY = ("Arial", 18, "bold")
FONT_CARD_TITLE = ("Arial", 13, "bold")
FONT_CARD_SUB = ("Arial", 9)
FONT_BANNER_BIG = ("Arial", 22, "bold")
FONT_BANNER_SUB = ("Arial", 12)

# ======================================================================
# Dimensions
# ======================================================================
WIN_WIDTH = 1000
WIN_HEIGHT = 562
TOPBAR_HEIGHT = 50
CARD_WIDTH = 300
CARD_HEIGHT = 180
CARD_PAD = 15
BOTTOM_HEIGHT = 100

# ======================================================================
# Canvas drawing helpers
# ======================================================================

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=12, **kwargs):
    """Draw a rounded rectangle on a Canvas and return its item IDs."""
    r = radius
    # Build a smooth polygon path for the rounded rectangle
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def draw_glow_rect(canvas, x1, y1, x2, y2, glow_color=GOLD, layers=3, **kwargs):
    """Draw a rectangle with a soft glow effect (layered outlines)."""
    items = []
    for i in range(layers, 0, -1):
        # Outer layers get more transparent by being wider and lighter
        offset = i * 2
        item = draw_rounded_rect(
            canvas,
            x1 - offset, y1 - offset,
            x2 + offset, y2 + offset,
            outline=glow_color, width=1,
            fill="",
        )
        items.append(item)
    # Draw the main rectangle on top
    main = draw_rounded_rect(canvas, x1, y1, x2, y2, **kwargs)
    items.append(main)
    return items


def create_themed_entry(parent, width=25, show=None):
    """Create a styled entry field matching the pirate theme."""
    return tk.Entry(
        parent, width=width, show=show, font=FONT_BODY,
        bg=BG_INPUT, fg=FG_TEXT, insertbackground=GOLD,
        relief="flat", highlightthickness=1,
        highlightbackground=BG_CARD, highlightcolor=GOLD,
    )


def create_themed_button(parent, text, command, bg=BTN_PRIMARY, fg="white",
                         width=20, font=FONT_BODY, **kwargs):
    """Create a styled button matching the pirate theme."""
    return tk.Button(
        parent, text=text, command=command, bg=bg, fg=fg,
        width=width, font=font, relief="flat", cursor="hand2",
        activebackground=bg, activeforeground=fg,
        bd=0, **kwargs,
    )
