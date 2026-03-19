"""Animated image-based card component for Lungi Launcher.

Each card renders a PNG background with smooth hover animations:
scale-up, glow border, dark overlay fade, and parallax shift.
Fully data-driven — no hardcoded content.
"""

import os
import sys
import tkinter as tk

from PIL import Image, ImageTk, ImageEnhance

from ui.theme import (
    GOLD, GOLD_DIM, FG_TEXT, FG_MUTED, BG_CARD,
    FONT_CARD_TITLE, FONT_CARD_SUB, FONT_TINY,
    CARD_WIDTH, CARD_HEIGHT,
)

# Toggle for console debug output
DEBUG = ("--debug" in sys.argv)

# Animation config
ANIM_DURATION_MS = 150
ANIM_STEP_MS = 16
SCALE_NORMAL = 1.0
SCALE_HOVER = 1.05
OVERLAY_NORMAL = 0.35
OVERLAY_HOVER = 0.15
GLOW_COLORS = ["#facc15", "#e6b800", "#cca300", "#b38f00"]
PARALLAX_PX = 4

# Resolve project root once (directory containing main.py)
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)


def _resolve_asset(relative_path):
    """Resolve a relative asset path against the project root."""
    return os.path.join(_PROJECT_ROOT, relative_path)


class ServerCard(tk.Canvas):
    """A clickable, animated server/mode card with PNG background.

    server_data: dict with keys title, desc, image, players.
    on_select:   callback(server_data) when clicked.
    """

    def __init__(self, master, server_data, on_select, is_selected=False):
        self._pad = 10
        cw = CARD_WIDTH + self._pad * 2
        ch = CARD_HEIGHT + self._pad * 2
        super().__init__(
            master, width=cw, height=ch,
            bg=master["bg"], highlightthickness=0, bd=0,
        )
        self.server_data = server_data
        self.on_select = on_select
        self.is_selected = is_selected

        # Animation state
        self._hover_t = 0.0
        self._target_t = 0.0
        self._anim_id = None
        self._glow_phase = 0
        self._glow_id = None
        self._mouse_x = CARD_WIDTH // 2
        self._mouse_y = CARD_HEIGHT // 2

        # Image references — stored on self to prevent GC
        self._src_image = None          # PIL Image (original)
        self._current_photo = None      # the ACTIVE ImageTk on canvas
        self._photo_cache = {}          # (scale, overlay) -> ImageTk
        self._image_loaded = False      # True if a real PNG was loaded

        self._load_source_image()
        self._draw()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Motion>", self._on_motion)
        self.bind("<Button-1>", self._on_click)

    # ------------------------------------------------------------------
    # Image loading
    # ------------------------------------------------------------------

    def _load_source_image(self):
        """Load the source PNG into a PIL Image, with robust fallback."""
        raw_path = self.server_data.get("image", "")
        abs_path = _resolve_asset(raw_path) if raw_path else ""

        try:
            if abs_path and os.path.isfile(abs_path):
                self._src_image = Image.open(abs_path).convert("RGB")
                self._image_loaded = True
                if DEBUG:
                    print(f"[Card] Loaded image: {abs_path}")
            else:
                if DEBUG:
                    print(f"[Card] Image not found: {abs_path!r}, using fallback")
                self._src_image = self._make_fallback_image()
        except Exception as exc:
            print(f"[Card] ERROR loading {abs_path!r}: {exc}")
            self._src_image = self._make_fallback_image()

    @staticmethod
    def _make_fallback_image():
        """Create a solid placeholder image when PNG is missing."""
        img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), (30, 41, 59))
        return img

    def _get_photo(self, scale, overlay_alpha):
        """Build a scaled + overlaid PhotoImage with caching."""
        s_key = round(scale, 2)
        a_key = round(overlay_alpha, 2)
        key = (s_key, a_key)
        if key in self._photo_cache:
            return self._photo_cache[key]

        try:
            w = int(CARD_WIDTH * scale)
            h = int(CARD_HEIGHT * scale)
            img = self._src_image.resize((w, h), Image.LANCZOS)

            if overlay_alpha > 0:
                dark = Image.new("RGB", (w, h), (0, 0, 0))
                img = Image.blend(img, dark, overlay_alpha)

            if scale > 1.01:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.0 + (scale - 1.0) * 2)

            photo = ImageTk.PhotoImage(img)
        except Exception as exc:
            print(f"[Card] ERROR building photo: {exc}")
            fallback = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), (30, 41, 59))
            photo = ImageTk.PhotoImage(fallback)

        # Bounded cache — but NEVER clear the current display photo
        if len(self._photo_cache) > 30:
            # Keep only the current key + this new one
            keep = {}
            if self._current_photo is not None:
                for k, v in self._photo_cache.items():
                    if v is self._current_photo:
                        keep[k] = v
                        break
            self._photo_cache = keep

        self._photo_cache[key] = photo
        return photo

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw(self):
        """Redraw everything based on current animation state."""
        self.delete("all")
        t = self._hover_t
        pad = self._pad
        w, h = CARD_WIDTH, CARD_HEIGHT

        # Interpolate values
        scale = SCALE_NORMAL + (SCALE_HOVER - SCALE_NORMAL) * t
        overlay = OVERLAY_NORMAL + (OVERLAY_HOVER - OVERLAY_NORMAL) * t

        # Parallax offset
        px = (self._mouse_x / w - 0.5) * PARALLAX_PX * t
        py = (self._mouse_y / h - 0.5) * PARALLAX_PX * t

        sw = int(w * scale)
        sh = int(h * scale)
        cx = pad + w // 2 + int(px)
        cy = pad + h // 2 + int(py)

        # Background image
        try:
            photo = self._get_photo(scale, overlay)
            self._current_photo = photo   # prevent GC
            self.create_image(cx, cy, image=photo, anchor="center")
        except Exception as exc:
            # Ultimate fallback: draw a colored rectangle
            print(f"[Card] draw fallback: {exc}")
            self.create_rectangle(
                pad, pad, pad + w, pad + h,
                fill=BG_CARD, outline=GOLD_DIM, width=1,
            )

        # If no real image, draw "NO IMAGE" indicator
        if not self._image_loaded:
            self.create_text(
                cx, cy - 15, text="NO IMAGE",
                font=("Arial", 10), fill=FG_MUTED,
            )

        # Glow border
        glow_alpha = t
        if self.is_selected:
            glow_alpha = 1.0

        if glow_alpha > 0.1:
            x1 = cx - sw // 2
            y1 = cy - sh // 2
            x2 = cx + sw // 2
            y2 = cy + sh // 2
            layers = max(1, int(3 * glow_alpha))
            color = GLOW_COLORS[self._glow_phase % len(GLOW_COLORS)]
            for i in range(layers, 0, -1):
                off = i * 2
                self.create_rectangle(
                    x1 - off, y1 - off, x2 + off, y2 + off,
                    outline=color, width=1,
                )
            border_color = GOLD if self.is_selected else GOLD_DIM
            self.create_rectangle(x1, y1, x2, y2, outline=border_color, width=2)

        # Text overlay (bottom area)
        d = self.server_data
        text_x = pad + w // 2 + int(px)
        base_y = pad + h + int(py)

        shadow = "#000000"
        self.create_text(text_x + 1, base_y - 54, text=d.get("title", ""),
                         font=FONT_CARD_TITLE, fill=shadow)
        self.create_text(text_x, base_y - 55, text=d.get("title", ""),
                         font=FONT_CARD_TITLE, fill=FG_TEXT)

        self.create_text(text_x + 1, base_y - 34, text=d.get("desc", ""),
                         font=FONT_CARD_SUB, fill=shadow)
        self.create_text(text_x, base_y - 35, text=d.get("desc", ""),
                         font=FONT_CARD_SUB, fill=FG_MUTED)

        players = d.get("players", 0)
        ptxt = f"\u25cf {players:,} online"
        pcolor = "#10b981" if players > 0 else FG_MUTED
        self.create_text(text_x + 1, base_y - 14, text=ptxt,
                         font=FONT_TINY, fill=shadow)
        self.create_text(text_x, base_y - 15, text=ptxt,
                         font=FONT_TINY, fill=pcolor)

    # ------------------------------------------------------------------
    # Animation engine
    # ------------------------------------------------------------------

    def _animate(self):
        """Step the hover animation toward _target_t."""
        steps = max(1, ANIM_DURATION_MS // ANIM_STEP_MS)
        step_size = 1.0 / steps

        if self._target_t > self._hover_t:
            self._hover_t = min(self._target_t, self._hover_t + step_size)
        elif self._target_t < self._hover_t:
            self._hover_t = max(self._target_t, self._hover_t - step_size)

        self._draw()

        if abs(self._hover_t - self._target_t) > 0.001:
            self._anim_id = self.after(ANIM_STEP_MS, self._animate)
        else:
            self._hover_t = self._target_t
            self._anim_id = None

    def _start_animation(self, target):
        """Begin animating toward a target hover value."""
        self._target_t = target
        if self._anim_id is None:
            self._animate()

    def _start_glow_cycle(self):
        """Cycle glow color while hovered."""
        if self._hover_t < 0.5 and not self.is_selected:
            self._glow_id = None
            return
        self._glow_phase = (self._glow_phase + 1) % len(GLOW_COLORS)
        self._draw()
        self._glow_id = self.after(400, self._start_glow_cycle)

    def _stop_glow_cycle(self):
        if self._glow_id is not None:
            self.after_cancel(self._glow_id)
            self._glow_id = None
        self._glow_phase = 0

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _on_enter(self, _event):
        self._start_animation(1.0)
        self._start_glow_cycle()
        self.configure(cursor="hand2")

    def _on_leave(self, _event):
        self._start_animation(0.0)
        self._stop_glow_cycle()
        self._mouse_x = CARD_WIDTH // 2
        self._mouse_y = CARD_HEIGHT // 2
        self.configure(cursor="")

    def _on_motion(self, event):
        self._mouse_x = max(0, min(CARD_WIDTH, event.x - self._pad))
        self._mouse_y = max(0, min(CARD_HEIGHT, event.y - self._pad))
        if self._hover_t > 0.3:
            self._draw()

    def _on_click(self, _event):
        self.on_select(self.server_data)

    def set_selected(self, selected):
        """Update selection state and redraw."""
        self.is_selected = selected
        if selected:
            self._start_glow_cycle()
        else:
            self._stop_glow_cycle()
        self._draw()
