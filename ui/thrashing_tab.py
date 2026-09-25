from collections import deque

import customtkinter as ctk
import psutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ui.theme import COLORS, get_font


class ThrashingTab(ctk.CTkFrame):
    """Lightweight live memory-pressure monitor for Day 2."""

    REFRESH_MS = 1000
    HISTORY_SIZE = 60

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.history = deque(maxlen=self.HISTORY_SIZE)
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.status_card = ctk.CTkFrame(self, fg_color=COLORS["mint_soft"], corner_radius=16,
                                        border_width=1, border_color=COLORS["mint_border"])
        self.status_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.status_var = ctk.StringVar(value="Normal")
        self.percent_var = ctk.StringVar(value="0.0% in use")
        self.advice_var = ctk.StringVar(value="Memory pressure is within the normal range.")
        ctk.CTkLabel(self.status_card, textvariable=self.status_var, font=get_font("title"),
                     text_color=COLORS["text"], anchor="w").pack(anchor="w", padx=18, pady=(14, 0))
        ctk.CTkLabel(self.status_card, textvariable=self.percent_var, font=get_font("body_bold"),
                     text_color=COLORS["blue"], anchor="w").pack(anchor="w", padx=18, pady=(2, 0))
        ctk.CTkLabel(self.status_card, textvariable=self.advice_var, font=get_font("body"),
                     text_color=COLORS["muted"], anchor="w").pack(anchor="w", padx=18, pady=(2, 14))

        info = ctk.CTkFrame(self, fg_color="transparent")
        info.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        info.grid_columnconfigure((0, 1), weight=1)
        self.available_var = ctk.StringVar(value="Available: —")
        self.total_var = ctk.StringVar(value="Total: —")
        for column, variable in ((0, self.available_var), (1, self.total_var)):
            card = ctk.CTkFrame(info, fg_color=COLORS["surface"], corner_radius=12,
                                border_width=1, border_color=COLORS["border_strong"])
            card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 6, 0))
            ctk.CTkLabel(card, textvariable=variable, font=get_font("body_bold"),
                         text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=12)

        panel = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=16,
                             border_width=1, border_color=COLORS["border_strong"])
        panel.grid(row=2, column=0, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(panel, text="RAM pressure history", font=get_font("body_bold"),
                     text_color=COLORS["text"], anchor="w").grid(row=0, column=0, sticky="w", padx=18, pady=(14, 0))
        self.figure = Figure(figsize=(5, 3), dpi=100, tight_layout={"pad": 0.8})
        self.figure.patch.set_facecolor(COLORS["surface"])
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=panel)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=6)

    @staticmethod
    def _status(percent):
        if percent >= 85:
            return "Thrashing", COLORS["red_soft"], COLORS["red"], "High memory pressure. Close heavy apps or use Optimize."
        if percent >= 75:
            return "Warning", COLORS["amber_soft"], COLORS["amber"], "Memory pressure is elevated. Consider freeing memory."
        return "Normal", COLORS["mint_soft"], COLORS["mint"], "Memory pressure is within the normal range."

    def _refresh(self):
        try:
            memory = psutil.virtual_memory()
            percent = float(memory.percent)
            self.history.append(percent)
            status, background, accent, advice = self._status(percent)
            self.status_var.set(status)
            self.percent_var.set(f"{percent:.1f}% in use")
            self.advice_var.set(advice)
            self.available_var.set(f"Available: {memory.available / (1024 ** 3):.2f} GB")
            self.total_var.set(f"Total: {memory.total / (1024 ** 3):.2f} GB")
            self.status_card.configure(fg_color=background, border_color=accent)
            self._draw_chart()
        except Exception as exc:
            self.status_var.set("Unavailable")
            self.advice_var.set(f"Memory readings unavailable: {exc}")
        try:
            self.after(self.REFRESH_MS, self._refresh)
        except Exception:
            pass

    def _draw_chart(self):
        values = list(self.history)
        self.ax.clear()
        if values:
            positions = range(1, len(values) + 1)
            self.ax.plot(positions, values, color=COLORS["blue"], linewidth=2.4)
            self.ax.fill_between(list(positions), values, 0, color=COLORS["blue"], alpha=0.12)
        self.ax.axhline(75, color=COLORS["amber"], linewidth=1, linestyle="--", alpha=0.8)
        self.ax.axhline(85, color=COLORS["red"], linewidth=1, linestyle="--", alpha=0.8)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0.5, max(1.5, len(values) + 0.5))
        self.ax.set_ylabel("In use (%)", fontsize=9, color=COLORS["muted"])
        self.ax.set_xlabel("Recent samples", fontsize=9, color=COLORS["muted"])
        self.ax.set_yticks((0, 25, 50, 75, 100))
        self.ax.grid(axis="y", color=COLORS["border"], linewidth=0.8)
        self.ax.set_facecolor(COLORS["surface"])
        self.ax.tick_params(colors=COLORS["muted"], labelsize=8, length=0)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.canvas.draw_idle()
