"""Sidebar mascot: a little RAM chip that idles, reacts and gives OS tips.

Lives in the sidebar (never covers content). All motion is cheap
`tk.Canvas` redraws: bobbing, blinking, pupil glances, jumps.
Click it for a random OS-theory tip. Respects `ANIM["enabled"]`.
"""

from __future__ import annotations

import math
import random
import time

import customtkinter as ctk

from ui import anim as anim_h
from ui.theme import COLORS, get_font

TIPS = [
    "Page fault in 6: reference, trap, find page, load frame, reset table, restart!",
    "OPT looks ahead, LRU looks back. OPT wins but needs a crystal ball.",
    "Belady: MORE frames, MORE faults?! Happens only with FIFO.",
    "Thrashing = CPU idle while the disk spins. Kill a process!",
    "Valid bit: 1 = in RAM, 0 = on disk.",
    "Compaction squishes holes into one big 660K hole.",
    "fault rate = faults / references. FIFO main set = 15/20 = 75%.",
    "Empty standby RAM, then defrag. That's the Optimize button!",
]

STATE_TINT = {
    "Normal": COLORS["mint"],
    "Warning": COLORS["amber"],
    "Thrashing": COLORS["red"],
}

PLAYFUL = [
    "RAM เต็มอีกแล้ว... กด Optimize ให้หน่อย!",
    "อย่าฆ่าผมนะ ไปฆ่า Chrome แทน",
    "ดิสก์หมุนจนเวียนหัวแล้ว",
    "วันนี้ page fault ไปกี่รอบแล้วน้า",
    "OPT เก่งสุด แต่ใช้จริงไม่ได้ เศร้าเลย",
    "FIFO โดน Belady แกล้งอีกแล้ว",
    "ขอยืม frame หน่อยสิ สัญญาจะคืน",
    "สถานะผมขึ้นกับอารมณ์ RAM ล้วนๆ",
]


class Mascot(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.state = "Normal"
        self.tint = STATE_TINT["Normal"]
        self._phase = 0.0
        self._blink = 0
        self._look = [0.0, 0.0]      # smoothed pupil offset (px)
        self._look_target = [0.0, 0.0]
        self._last_mouse = 0.0
        self._jump_total = 0
        self._jump_n = 0
        self._deck: list[str] = []
        self._hold_until = 0.0

        self.bubble = ctk.CTkLabel(
            self, text="Hi! I'm Chip, your RAM buddy!",
            text_color=COLORS["text"],
            fg_color=COLORS["surface"], bg_color="transparent",
            corner_radius=10, width=160, height=54,
            wraplength=150, justify="left",
            font=get_font("hint"), anchor="w",
        )
        # Always visible with fixed size: swapping text never shifts layout.
        self.bubble.pack(pady=(0, 6))
        self.canvas = ctk.CTkCanvas(
            self, width=120, height=104, bg=parent.cget("fg_color") if self._bg(parent) else "#FFFFFF",
            highlightthickness=0,
        )
        try:
            self.canvas.configure(bg=COLORS["sidebar"])
        except Exception:
            pass
        self.canvas.pack()
        try:
            self.canvas.bind("<Button-1>", lambda e: self.say(random.choice(TIPS)))
        except Exception:
            pass
        # Follow the cursor: handler only stores a target (no redraw here).
        try:
            top = self.winfo_toplevel()
            top.bind("<Motion>", self._on_mouse, add="+")
        except Exception:
            pass
        self._paint()
        self._idle_loop()
        self._chatter_loop()

    @staticmethod
    def _bg(parent):
        try:
            parent.cget("fg_color")
            return True
        except Exception:
            return False

    # ---------- public ----------

    def react(self, state: str, pct: float | None = None):
        if state == self.state:
            return
        was_bad = self.state in ("Warning", "Thrashing")
        self.state = state
        self.tint = STATE_TINT.get(state, STATE_TINT["Normal"])
        if state == "Thrashing":
            self._jump()
            self.say(f"Thrashing! RAM {pct:.0f}% — close something!" if pct is not None else "Thrashing! Close something!")
        elif state == "Warning":
            self.say(f"Getting tight... {pct:.0f}%" if pct is not None else "Getting tight...")
        elif was_bad:
            self._jump()
            self.say("Phew, back to normal!")
        self._paint()

    def celebrate(self, text: str):
        self._jump()
        self.say(text)

    def say(self, text: str, hold_ms: int = 9000):
        # Priority message: holds the bubble, then chatter resumes.
        try:
            self.bubble.configure(text=text)
        except Exception:
            return
        try:
            self._hold_until = time.monotonic() + hold_ms / 1000.0
        except Exception:
            pass

    def _chatter_loop(self):
        try:
            if self._alive():
                try:
                    if time.monotonic() >= self._hold_until:
                        if not self._deck:
                            self._deck = TIPS + PLAYFUL
                            random.shuffle(self._deck)
                        self.bubble.configure(text=self._deck.pop())
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self.after(7000, self._chatter_loop)
        except Exception:
            pass

    # ---------- internals ----------

    def _jump(self):
        self._jump_total = 12
        self._jump_n = 12

    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    def _on_mouse(self, event):
        # Cheap: store a clamped target; the 80ms loop eases toward it.
        try:
            cx = self.canvas.winfo_rootx() + 60
            cy = self.canvas.winfo_rooty() + 50
            dx, dy = event.x_root - cx, event.y_root - cy
            dist = math.hypot(dx, dy)
            if dist < 1e-6:
                return
            mag = min(3.0, dist / 12.0)  # gentle: full deflection past ~36px
            self._look_target = [dx / dist * mag, dy / dist * mag]
            self._last_mouse = time.monotonic()
        except Exception:
            pass

    def _idle_loop(self):
        try:
            if self._alive():
                self._phase += 0.25
                # blink every ~3s for 2 frames
                if self._blink > 0:
                    self._blink -= 1
                elif random.random() < 0.008:
                    self._blink = 2
                # ease pupils toward target (gentle); drift home when idle
                try:
                    if time.monotonic() - self._last_mouse > 4.0:
                        self._look_target = [0.0, 0.0]
                        if random.random() < 0.01:
                            self._look_target = [float(random.choice((-2, 0, 0, 2))), 0.0]
                    for i in (0, 1):
                        self._look[i] += (self._look_target[i] - self._look[i]) * 0.25
                except Exception:
                    pass
                if self._jump_n > 0:
                    self._jump_n -= 1
                if anim_h.enabled():
                    self._paint()
                elif self._blink == 0 and self._jump_n == 0:
                    pass
                else:
                    self._paint()
        except Exception:
            pass
        try:
            self.after(80, self._idle_loop)
        except Exception:
            pass

    def _dy(self) -> int:
        dy = int(2.5 * math.sin(self._phase))
        if self._jump_n > 0 and self._jump_total > 0:
            done = 1.0 - self._jump_n / self._jump_total
            dy -= int(10 * math.sin(math.pi * max(0.0, min(1.0, done))))
        return dy

    def _paint(self):
        c = self.canvas
        try:
            c.delete("all")
            dy = self._dy()
            # shadow
            c.create_oval(38, 92 + dy // 3, 82, 98 + dy // 3, fill="#E5EAF2", outline="")
            # pins
            for y in (36, 52, 68):
                c.create_line(22, y + dy, 32, y + dy, fill="#9AA5B8", width=4)
                c.create_line(88, y + dy, 98, y + dy, fill="#9AA5B8", width=4)
            # body
            c.create_rectangle(32, 22 + dy, 88, 82 + dy, fill="#FFFFFF",
                               outline=self.tint, width=3)
            # notch
            c.create_arc(52, 22 + dy, 68, 34 + dy, start=180, extent=180,
                         fill=self.tint, outline="")
            # blush
            try:
                blush = anim_h.hex_lerp(self.tint, "#FFFFFF", 0.6)
            except Exception:
                blush = self.tint
            c.create_oval(38, 58 + dy, 46, 64 + dy, fill=blush, outline="")
            c.create_oval(74, 58 + dy, 82, 64 + dy, fill=blush, outline="")
            # eyes
            if self._blink > 0:
                c.create_line(44, 50 + dy, 54, 50 + dy, fill="#172033", width=2)
                c.create_line(66, 50 + dy, 76, 50 + dy, fill="#172033", width=2)
            else:
                lx, ly = int(round(self._look[0])), int(round(self._look[1]))
                for ex in (49, 71):
                    c.create_oval(ex - 6, 44 + dy, ex + 6, 56 + dy, fill="#FFFFFF", outline="#172033", width=1)
                    c.create_oval(ex - 2 + lx, 47 + dy + ly, ex + 4 + lx, 53 + dy + ly,
                                  fill="#172033", outline="")
            # mouth (flat when Thrashing, smile otherwise)
            if self.state == "Thrashing":
                c.create_line(54, 68 + dy, 66, 68 + dy, fill="#172033", width=2)
            else:
                c.create_arc(54, 60 + dy, 66, 70 + dy, start=200, extent=140,
                             outline="#172033", width=2, style="arc")
        except Exception:
            pass
