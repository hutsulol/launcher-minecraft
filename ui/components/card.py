"""Animated image-based card component for Lungi Launcher.

Each card renders a PNG background with smooth hover animations:
scale-up, glow border, dark overlay fade, and parallax shift.
Fully data-driven — no hardcoded content.
"""

import os
import tkinter as tk

from PIL import Image, ImageTk, ImageEnhance, ImageFilter

from ui.theme import (
    GOLD, GOLD_DIM, FG_TEXT, FG_MUTED,
    FONT_CARD_TITLE, FONT_CARD_SUB, FONT_TINY,
    CARD_WIDTH, CARD_HEIGHT, BG_DEEP,
)

# Animation config
ANIM_DURATION_MS = 150       # total transition time
ANIM_STEP_MS = 16            # ~60 fps
SCALE_NORMAL = 1.0
SCALE_HOVER = 1.05
OVERLAY_NORMAL = 0.35        # dark overlay opacity (0-1)
OVERLAY_HOVER = 0.15         # lighter on hover to reveal image
GLOW_COLORS = ["#facc15", "#e6b800", "#cca300", "#b38f00"]
PARALLAX_PX = 4              # max pixel shift on mouse move


class ServerCard(tk.Canvas):
    """A clickable, animated server/mode card with PNG background.

    server_data: dict with keys title, desc, image, players.
    on_select:   callback(server_data) when clicked.
    """

    def __init__(self, master, server_data, on_select, is_selected=False):
        # Allocate extra canvas space for scale-up + glow
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
        self._hover_t = 0.0          # 0 = normal, 1 = fully hovered
        self._target_t = 0.0
        self._anim_id = None
        self._glow_phase = 0         # for cycling glow
        self._glow_id = None
        self._mouse_x = CARD_WIDTH // 2
        self._mouse_y = CARD_HEIGHT // 2

        # Image caches (prevent GC)
        self._src_image = None       # PIL Image (original size)
        self._photo_cache = {}       # scale -> ImageTk.PhotoImage

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
        """Load the source PNG into a PIL Image."""
        path = self.server_data.get("image", "")
        if path and os.path.isfile(path):
            self._src_image = Image.open(path).convert("RGB")
        else:
            self._src_image = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), (30, 41, 59))

    def _get_photo(self, scale, overlay_alpha):
        """Build a scaled + overlaid PhotoImage, with caching by rounded params."""
        # Round to avoid too many cache entries
        s_key = round(scale, 3)
        a_key = round(overlay_alpha, 2)
        key = (s_key, a_key)
        if key in self._photo_cache:
            return self._photo_cache[key]

        w = int(CARD_WIDTH * scale)
        h = int(CARD_HEIGHT * scale)
        img = self._src_image.resize((w, h), Image.LANCZOS)

        # Apply dark overlay by blending with black
        if overlay_alpha > 0:
            dark = Image.new("RGB", (w, h), (0, 0, 0))
            img = Image.blend(img, dark, overlay_alpha)

        # Slight brightness boost on hover
        if scale > 1.01:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.0 + (scale - 1.0) * 2)

        photo = ImageTk.PhotoImage(img)

        # Keep cache bounded
        if len(self._photo_cache) > 20:
            self._photo_cache.clear()
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

        # Interpolate values
        scale = SCALE_NORMAL + (SCALE_HOVER - SCALE_NORMAL) * t
        overlay = OVERLAY_NORMAL + (OVERLAY_HOVER - OVERLAY_NORMAL) * t

        # Parallax offset based on mouse position
        px = (self._mouse_x / CARD_WIDTH - 0.5) * PARALLAX_PX * t
        py = (self._mouse_y / CARD_HEIGHT - 0.5) * PARALLAX_PX * t

        # Scaled image dimensions
        sw = int(CARD_WIDTH * scale)
        sh = int(CARD_HEIGHT * scale)

        # Center the scaled image in the padded canvas
        cx = pad + CARD_WIDTH // 2 + int(px)
        cy = pad + CARD_HEIGHT // 2 + int(py)

        photo = self._get_photo(scale, overlay)
        self.create_image(cx, cy, image=photo, anchor="center")

        # Glow border (visible when hovered or selected)
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
        text_x = pad + CARD_WIDTH // 2 + int(px)
        base_y = pad + CARD_HEIGHT + int(py)

        # Text shadow for readability
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
