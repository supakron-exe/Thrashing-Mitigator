"""Sidebar status card: pulse dot + static RAM bar + shake.

Only the dot rings animate per-frame (cheap canvas ovals). The bar is
static; borders use muted state tones so the card stays calm.
Respects `ANIM["enabled"]` kill-switch (static fallback).
"""

from __future__ import annotations

import customtkinter as ctk

from ui import anim as anim_h
from ui.theme import ANIM, COLORS, get_font

STATE_COLORS = {
    "Normal": COLORS["mint"],
    "Warning": COLORS["amber"],
    "Thrashing": COLORS["red"],
}

W = 156  # inner drawing width


def _muted_border(c: str) -> str:
    try:
        return anim_h.hex_lerp(c, "#9AA5B8", 0.55)
    except Exception:
        return c


def _muted_fill(c: str) -> str:
    try:
        return anim_h.hex_lerp(c, "#FFFFFF", 0.30)
    except Exception:
        return c


def _state_of(pct: float) -> str:
    if pct >= 85:
        return "Thrashing"
    if pct >= 75:
        return "Warning"
    return "Normal"


class StatusCard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["surface_2"],
            corner_radius=12,
            border_width=1,
            border_color=_muted_border(COLORS["mint"]),
        )
        self.state = "Normal"
        self.color = COLORS["mint"]
        self.pct = 0.0
        self.shown_pct = 0.0
        self._rings: list[float] = []  # radii 6..15
        self._shake_n = 0
        self._tick_n = 0
        self._border_cur = _muted_border(COLORS["mint"])

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 0))
        self.dot_canvas = ctk.CTkCanvas(
            top, width=30, height=30, bg=COLORS["surface_2"],
            highlightthickness=0,
        )
        self.dot_canvas.pack(side="left")
        text = ctk.CTkFrame(top, fg_color="transparent")
        text.pack(side="left", padx=(6, 0), anchor="center")
        self.state_label = ctk.CTkLabel(
            text, text="Checking...", text_color=COLORS["text"],
            font=get_font("body_bold"), anchor="w",
        )
        self.state_label.pack(anchor="w")
        self.ram_label = ctk.CTkLabel(
            text, text="RAM --%", text_color=COLORS["muted"],
            font=get_font("metric_hint"), anchor="w",
        )
        self.ram_label.pack(anchor="w")

        self.bar_canvas = ctk.CTkCanvas(
            self, width=W, height=12, bg=COLORS["surface_2"],
            highlightthickness=0,
        )
        self.bar_canvas.pack(fill="x", padx=10, pady=(6, 10))

        self._draw_dot()
        self._draw_bar()
        self._pulse_loop()

    # ---------- public ----------

    def set_sample(self, pct: float):
        try:
            pct = max(0.0, min(100.0, float(pct)))
        except Exception:
            return
        self.pct = pct
        new_state = _state_of(pct)
        if new_state != self.state:
            self._change_state(new_state)
        # % count-up (cheap label text only)
        start = self.shown_pct
        self.shown_pct = pct
        if anim_h.enabled():
            anim_h.count_up(
                self, 300, start, pct,
                lambda v: f"RAM {v:.1f}%", self._set_ram_text,
            )
        else:
            self._set_ram_text(f"RAM {pct:.1f}%")
        self._draw_bar()

    # ---------- internals ----------

    def _set_ram_text(self, text):
        try:
            self.ram_label.configure(text=text)
        except Exception:
            pass

    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    def _change_state(self, new_state: str):
        old_muted = self._border_cur
        self.state = new_state
        self.color = STATE_COLORS[new_state]
        new_muted = _muted_border(self.color)
        try:
            self.state_label.configure(text=new_state, text_color=self.color)
        except Exception:
            pass
        # border fade muted old -> muted new (no layout change)
        def _frame(t):
            try:
                c = anim_h.hex_lerp(old_muted, new_muted, t)
                self._border_cur = c
                self.configure(border_color=c)
            except Exception:
                pass

        anim_h.tween(self, 300, _frame, key="footer-border")
        # burst rings + shake when entering Thrashing
        self._rings.extend([6.0, 6.0, 6.0])
        if new_state == "Thrashing":
            self._shake_n = 10

    def _dx(self) -> int:
        if self._shake_n <= 0:
            return 0
        mag = 3 if self._shake_n > 5 else 2
        return mag if self._shake_n % 2 == 0 else -mag

    def _pulse_loop(self):
        try:
            if self._alive():
                self._tick_n += 1
                if anim_h.enabled():
                    if self._tick_n % 5 == 0:
                        self._rings.append(6.0)
                    self._rings = [r + 0.6 for r in self._rings if r < 15.0]
                    self._rings = self._rings[-8:]
                    self._draw_dot()
                    if self._shake_n > 0:
                        self._shake_n -= 1
                        self._draw_bar()
                else:
                    if self._shake_n > 0:
                        self._shake_n = 0
                    self._rings = []
                    self._draw_dot()
        except Exception:
            pass
        try:
            self.after(60, self._pulse_loop)
        except Exception:
            pass

    def _draw_dot(self):
        c = self.dot_canvas
        try:
            c.delete("all")
            dx = self._dx()
            cx, cy = 15 + dx, 15
            for r in self._rings:
                k = (r - 6.0) / 9.0  # 0 fresh -> 1 faded
                try:
                    col = anim_h.hex_lerp(self.color, COLORS["surface_2"], k)
                except Exception:
                    col = self.color
                c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=col, width=2)
            c.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=self.color, outline="")
        except Exception:
            pass

    def _draw_bar(self):
        c = self.bar_canvas
        try:
            c.delete("all")
            w = c.winfo_width()
            if w < 10:
                w = W
            h = 12
            dx = self._dx()
            # track
            c.create_rectangle(0, 2, w, h - 2, fill=COLORS["border"], outline="")
            fill_w = w * max(0.0, min(1.0, self.shown_pct / 100.0 if self.shown_pct else self.pct / 100.0))
            if fill_w > 1:
                # static solid fill in a muted state tone (no marching stripes)
                c.create_rectangle(dx, 2, dx + fill_w, h - 2, fill=_muted_fill(self.color), outline="")
        except Exception:
            pass
