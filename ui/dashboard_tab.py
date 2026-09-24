import gc
from collections import deque

import customtkinter as ctk
import psutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from ui.theme import COLORS


class DashboardTab(ctk.CTkFrame):
    """Live RAM dashboard with recent history and a memory distribution chart."""

    REFRESH_MS = 2000
    HISTORY_SIZE = 60

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.history = deque(maxlen=self.HISTORY_SIZE)
        self.total_bytes = 0
        self.used_bytes = 0
        self.available_bytes = 0
        self.percent = 0.0
        self._build_ui()
        self.refresh()
        self.after(self.REFRESH_MS, self._auto_refresh)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=7, minsize=380)
        self.grid_columnconfigure(1, weight=3, minsize=210)
        self.grid_rowconfigure(2, weight=1)

        heading = ctk.CTkFrame(self, fg_color="transparent")
        heading.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(
            heading, text="Memory at a glance", text_color=COLORS["text"],
            font=ctk.CTkFont(size=16, weight="bold"), anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            heading, text="Physical memory · live readings", text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11), anchor="e",
        ).pack(side="right")

        metrics = ctk.CTkFrame(self, fg_color="transparent")
        metrics.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        metrics.grid_columnconfigure((0, 1, 2), weight=1, uniform="metric")
        self.total_var = ctk.StringVar(value="—")
        self.used_var = ctk.StringVar(value="—")
        self.available_var = ctk.StringVar(value="—")
        self.total_hint_var = ctk.StringVar(value="—")
        self.used_hint_var = ctk.StringVar(value="—")
        self.available_hint_var = ctk.StringVar(value="—")
        self._add_metric(metrics, 0, "TOTAL RAM", self.total_var, self.total_hint_var, COLORS["blue"])
        self._add_metric(metrics, 1, "IN USE", self.used_var, self.used_hint_var, COLORS["pink"])
        self._add_metric(metrics, 2, "AVAILABLE", self.available_var, self.available_hint_var, COLORS["mint"])

        self._build_history_panel()
        self._build_right_rail()

    def _add_metric(self, parent, column, title, value, hint, accent):
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["surface"], corner_radius=15,
            border_width=1, border_color=COLORS["border"],
        )
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))
        ctk.CTkFrame(card, width=4, height=38, fg_color=accent, corner_radius=2).pack(
            side="left", padx=(14, 12), pady=14,
        )
        text = ctk.CTkFrame(card, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True, pady=10, padx=(0, 10))
        ctk.CTkLabel(
            text, text=title, text_color=COLORS["muted"],
            font=ctk.CTkFont(size=9, weight="bold"), anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            text, textvariable=value, text_color=COLORS["text"],
            font=ctk.CTkFont(size=19, weight="bold"), anchor="w",
        ).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(
            text, textvariable=hint, text_color=COLORS["muted"],
            font=ctk.CTkFont(size=9), anchor="w",
        ).pack(anchor="w", pady=(1, 0))

    def _build_history_panel(self):
        panel = ctk.CTkFrame(
            self, fg_color=COLORS["surface"], corner_radius=16,
            border_width=1, border_color=COLORS["border"],
        )
        panel.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(15, 0))
        ctk.CTkLabel(
            header, text="RAM usage history", text_color=COLORS["text"],
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(side="left")
        self.history_summary_var = ctk.StringVar(value="Now: —")
        ctk.CTkLabel(
            header, textvariable=self.history_summary_var, text_color=COLORS["blue"],
            font=ctk.CTkFont(size=9, weight="bold"),
        ).pack(side="right")

        self.figure = Figure(figsize=(5.2, 3.3), dpi=100, tight_layout=True)
        self.figure.patch.set_facecolor(COLORS["surface"])
        self.history_ax = self.figure.add_subplot(111)
        self.history_canvas = FigureCanvasTkAgg(self.figure, master=panel)
        self.history_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 6))

    def _build_right_rail(self):
        rail = ctk.CTkFrame(self, fg_color="transparent")
        rail.grid(row=2, column=1, sticky="nsew", padx=(8, 0))
        rail.grid_columnconfigure(0, weight=1)
        rail.grid_rowconfigure(0, weight=5)
        rail.grid_rowconfigure(1, weight=5)

        distribution = ctk.CTkFrame(
            rail, fg_color=COLORS["surface"], corner_radius=16,
            border_width=1, border_color=COLORS["border"],
        )
        distribution.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        distribution.grid_columnconfigure(0, weight=1)
        distribution.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(
            distribution, text="Memory distribution", text_color=COLORS["text"],
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=17, pady=(15, 0))

        self.available_legend_var = ctk.StringVar(value="Available: —")
        ctk.CTkLabel(
            distribution, textvariable=self.available_legend_var,
            text_color=COLORS["pink"], font=ctk.CTkFont(size=9), anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=17, pady=(4, 0))

        self.donut_figure = Figure(figsize=(1.9, 1.25), dpi=100, tight_layout=True)
        self.donut_figure.patch.set_facecolor(COLORS["surface"])
        self.donut_ax = self.donut_figure.add_subplot(111)
        self.donut_canvas = FigureCanvasTkAgg(self.donut_figure, master=distribution)
        self.donut_canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew", padx=7, pady=(0, 0))

        actions = ctk.CTkFrame(
            rail, fg_color=COLORS["surface"], corner_radius=16,
            border_width=1, border_color=COLORS["border"],
        )
        actions.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        ctk.CTkLabel(
            actions, text="Quick actions", text_color=COLORS["text"],
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 9))
        ctk.CTkButton(
            actions, text="Optimize now", height=38, corner_radius=10,
            fg_color=COLORS["blue"], hover_color="#1266C7",
            font=ctk.CTkFont(size=12, weight="bold"), command=self.optimize_now,
        ).pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkButton(
            actions, text="Refresh readings", height=34, corner_radius=10,
            fg_color=COLORS["blue_soft"], hover_color="#D8E9FF",
            text_color=COLORS["blue"], font=ctk.CTkFont(size=11, weight="bold"),
            command=self.refresh,
        ).pack(fill="x", padx=14)
        self.status_var = ctk.StringVar(value="Auto refresh: every 2 seconds.")
        self.status_label = ctk.CTkLabel(
            actions, textvariable=self.status_var, text_color=COLORS["muted"],
            font=ctk.CTkFont(size=8), wraplength=190, justify="left", anchor="w",
        )
        self.status_label.pack(fill="x", padx=15, pady=(4, 2))

    @staticmethod
    def _to_gb(byte_count):
        return byte_count / (1024 ** 3)

    def refresh(self):
        memory = psutil.virtual_memory()
        self.total_bytes = memory.total
        self.available_bytes = min(memory.available, self.total_bytes)
        self.used_bytes = max(self.total_bytes - self.available_bytes, 0)
        self.percent = (self.used_bytes / self.total_bytes * 100) if self.total_bytes else 0.0
        self.history.append((self.used_bytes, self.total_bytes))

        total_gb = self._to_gb(self.total_bytes)
        used_gb = self._to_gb(self.used_bytes)
        available_gb = self._to_gb(self.available_bytes)
        available_percent = max(100.0 - self.percent, 0.0)
        self.total_var.set(f"{total_gb:.2f} GB")
        self.used_var.set(f"{used_gb:.2f} GB")
        self.available_var.set(f"{available_gb:.2f} GB")
        self.total_hint_var.set("100.0% of installed RAM")
        self.used_hint_var.set(f"{self.percent:.1f}% occupied")
        self.available_hint_var.set(f"{available_percent:.1f}% free")
        self.history_summary_var.set(f"Now: {used_gb:.2f} GB · {self.percent:.1f}%")
        self.available_legend_var.set(
            f"Available: {available_gb:.2f} GB · {available_percent:.1f}%"
        )
        self._draw_history()
        self._draw_donut()

    def _draw_history(self):
        self.history_ax.clear()
        samples = list(self.history)
        values = [used / total * 100 if total else 0.0 for used, total in samples]
        positions = list(range(1, len(values) + 1))
        if values:
            self.history_ax.plot(positions, values, color=COLORS["blue"], linewidth=2.4)
            self.history_ax.fill_between(positions, values, 0, color=COLORS["blue"], alpha=0.12)
            self.history_ax.scatter(positions[-1:], values[-1:], color=COLORS["pink"], s=22, zorder=3)
        if len(values) < 3:
            self.history_ax.text(
                0.98, 0.96, "Collecting live samples...",
                transform=self.history_ax.transAxes, ha="right", va="top",
                color=COLORS["muted"], fontsize=8,
            )
        self.history_ax.set_ylim(0, 100)
        self.history_ax.set_xlim(0.5, len(values) + 0.5)
        ticks = (0, 25, 50, 75, 100)
        total_gb = self._to_gb(self.total_bytes)
        tick_labels = [f"{tick}%\n{total_gb * tick / 100:.2f} GB" for tick in ticks]
        self.history_ax.set_yticks(ticks, tick_labels)
        self.history_ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
        self.history_ax.set_ylabel("In use (%) · GB", fontsize=9, color=COLORS["muted"])
        self.history_ax.set_xlabel("Recent samples · one every 2 seconds", fontsize=9, color=COLORS["muted"])
        self.history_ax.grid(axis="y", color=COLORS["border"], linewidth=0.8)
        self.history_ax.set_facecolor(COLORS["surface"])
        self.history_ax.tick_params(colors=COLORS["muted"], labelsize=7, length=0)
        for spine in self.history_ax.spines.values():
            spine.set_visible(False)
        self.history_canvas.draw_idle()

    def _draw_donut(self):
        self.donut_ax.clear()
        self.donut_ax.pie(
            [self.used_bytes, self.available_bytes],
            startangle=90,
            counterclock=False,
            colors=[COLORS["blue"], COLORS["pink"]],
            wedgeprops={"width": 0.28, "edgecolor": COLORS["surface"], "linewidth": 3},
        )
        self.donut_ax.text(0, 0.04, f"{self.percent:.1f}%", ha="center", va="center",
                           color=COLORS["text"], fontsize=16, fontweight="bold")
        self.donut_ax.text(0, -0.25, f"{self._to_gb(self.used_bytes):.2f} GB",
                           ha="center", va="center", color=COLORS["muted"], fontsize=7)
        self.donut_ax.axis("equal")
        self.donut_canvas.draw_idle()

    def optimize_now(self):
        collected = gc.collect()
        self.refresh()
        self.status_var.set(
            f"Cleaned {collected} Python objects. RAM now: "
            f"{self._to_gb(self.used_bytes):.2f} GB · {self.percent:.1f}% in use."
        )

    def _auto_refresh(self):
        if self.winfo_exists():
            self.refresh()
            self.after(self.REFRESH_MS, self._auto_refresh)
