from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk

from ui.dashboard_tab import DashboardTab
from ui.process_tab import ProcessTab
from ui.thrashing_tab import ThrashingTab
from ui.footer_status import StatusCard
from ui.icons import get_nav_icon
from ui.mascot import Mascot
from ui.theme import ANIM, COLORS, apply_theme, get_font
from ui import anim as anim_h


PAGE_INFO = {
    "Overview": ("Memory overview", "Live system memory and quick actions"),
    "Thrashing": ("Thrashing monitor", "Memory pressure signals and guidance"),
    "Processes": ("Processes", "Inspect memory use by running process"),
    "Simulator": ("Page replacement simulator", "Compare page replacement algorithms"),
    "Paging + Partition": ("Paging and partition", "Translate addresses and place processes"),
}


class App(ctk.CTk):
    """Main window for the Thrashing Mitigator demo."""

    def __init__(self):
        apply_theme()
        super().__init__()
        self.sidebar_logo = self._load_logo()
        self.title("Thrashing Mitigator")
        self.geometry("920x680")
        self.minsize(900, 640)
        self.configure(fg_color=COLORS["background"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._current_page = None
        self._live_phase = 0

        self._build_sidebar()
        self._build_main_area()
        self._build_pages()
        self._show_page("Overview")
        self._pulse_live()
        self._refresh_footer_status()

    def _load_logo(self):
        logo_path = (
            Path(__file__).resolve().parent.parent
            / "logo"
            / "Gemini_Generated_Image_7dmlu97dmlu97dml.png"
        )
        if not logo_path.is_file():
            return None

        with Image.open(logo_path) as source:
            logo = source.convert("RGBA")
        visible_bounds = logo.getchannel("A").getbbox()
        if visible_bounds:
            logo = logo.crop(visible_bounds)

        self._window_icon = ImageTk.PhotoImage(
            self._fit_image(logo, (32, 32)), master=self,
        )
        self.iconphoto(True, self._window_icon)
        return ctk.CTkImage(
            light_image=logo,
            dark_image=logo,
            size=self._fit_ctk_size(logo.size, 42),
        )

    @staticmethod
    def _fit_ctk_size(native, box):
        w, h = native
        if w <= 0 or h <= 0:
            return (box, box)
        scale = box / max(w, h)
        return (max(1, int(round(w * scale))), max(1, int(round(h * scale))))

    @staticmethod
    def _fit_image(image, bounds):
        fitted = image.copy()
        fitted.thumbnail(bounds, Image.Resampling.LANCZOS)
        return fitted

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLORS["sidebar"],
                               border_width=1, border_color=COLORS["border"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(3, weight=1)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(24, 14))
        # --- subtle zone divider: brand | nav ---
        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border_strong"]).pack(
            fill="x", padx=20, pady=(0, 12)
        )
        if self.sidebar_logo is not None:
            ctk.CTkLabel(
                brand,
                text="",
                image=self.sidebar_logo,
                width=42,
                height=42,
                fg_color="transparent",
            ).pack(side="left", anchor="center")
        else:
            ctk.CTkLabel(
                brand,
                text="TM",
                width=42,
                height=42,
                corner_radius=13,
                fg_color=COLORS["blue"],
                text_color="white",
                font=get_font("title"),
            ).pack(side="left", anchor="center")
        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        # NOTE: no fixed width/height, no pack_propagate(False), no place():
        # two stacked packs auto-size, so 100%/125% scaling never overlaps.
        brand_text.pack(side="left", padx=(10, 0), anchor="center")
        ctk.CTkLabel(
            brand_text, text="Thrashing", text_color=COLORS["text"],
            font=get_font("title"), anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand_text, text="MITIGATOR", text_color=COLORS["muted"],
            font=get_font("caption"), anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            sidebar, text="WORKSPACE", text_color=COLORS["muted"],
            font=get_font("caption"), anchor="w",
        ).pack(fill="x", padx=22, pady=(0, 8))

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.pack(fill="x", padx=10)
        self.nav_buttons = {}
        self.nav_icons = {}
        for label in (
            "Overview",
            "Thrashing",
            "Processes",
            "Simulator",
            "Paging + Partition",
        ):
            icon = get_nav_icon(label)
            if icon is not None:
                self.nav_icons[label] = icon  # keep ref: no GC disappearing
            button = ctk.CTkButton(
                nav,
                text=label if icon is not None else f"  \u2022   {label}",
                image=icon,
                compound="left",
                anchor="w",
                height=44,
                corner_radius=12,
                fg_color=COLORS["sidebar"],
                hover_color=COLORS["blue_soft"],
                text_color=COLORS["muted"],
                font=get_font("nav"),
                command=lambda page=label: self._show_page(page),
            )
            button.pack(fill="x", pady=3)
            button.bind("<Enter>", lambda e, b=button: self._nav_hover(b, True))
            button.bind("<Leave>", lambda e, b=button: self._nav_hover(b, False))
            self.nav_buttons[label] = button

        # Bottom stack (side=bottom: first packed = bottommost).
        # Top-to-bottom result: mascot, divider, status card.
        self.footer_card = StatusCard(sidebar)
        self.footer_card.pack(side="bottom", fill="x", padx=12, pady=(0, 12))
        # --- subtle zone divider: companion zone | nav ---
        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border_strong"]).pack(
            side="bottom", fill="x", padx=20, pady=(0, 10)
        )
        self.mascot = Mascot(sidebar)
        self.mascot.pack(side="bottom", pady=(0, 4))
        # compat handles for tests/tools
        self.footer_state = self.footer_card.state_label
        self.footer_ram = self.footer_card.ram_label

    def _build_main_area(self):
        main = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew", padx=(16, 16), pady=12)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent", height=62)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)
        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")
        self.page_title = ctk.CTkLabel(
            title_block, text="Memory overview", text_color=COLORS["text"],
            font=get_font("display"), anchor="w",
        )
        self.page_title.pack(anchor="w")
        self.page_subtitle = ctk.CTkLabel(
            title_block, text="Live system memory and quick actions", text_color=COLORS["muted"],
            font=get_font("subtitle"), anchor="w",
        )
        self.page_subtitle.pack(anchor="w", pady=(2, 0))

        live = ctk.CTkFrame(
            header, fg_color=COLORS["mint_soft"], corner_radius=12,
            border_width=1, border_color=COLORS["mint_border"],
        )
        live.grid(row=0, column=1, sticky="e", padx=(10, 0))
        self.live_dot = ctk.CTkLabel(
            live, text="\u25cf  LIVE", text_color="#21866E",
            font=get_font("caption"),
        )
        self.live_dot.pack(padx=12, pady=9)

        self.page_host = ctk.CTkFrame(main, fg_color="transparent")
        self.page_host.grid(row=1, column=0, sticky="nsew")
        self.page_host.grid_rowconfigure(0, weight=1)
        self.page_host.grid_columnconfigure(0, weight=1)

    def _build_pages(self):
        self.pages = {"Overview": DashboardTab(self.page_host)}
        self.pages["Overview"].mascot = self.mascot
        self.pages["Overview"].grid(row=0, column=0, sticky="nsew")

        self.pages["Thrashing"] = ThrashingTab(self.page_host)
        self.pages["Processes"] = ProcessTab(self.page_host)
        self.pages["Thrashing"].grid(row=0, column=0, sticky="nsew")
        self.pages["Processes"].grid(row=0, column=0, sticky="nsew")

        descriptions = {
            "Simulator": "FIFO, LRU, OPT, LFU, and MFU simulations are part of Day 3.",
            "Paging + Partition": "Address translation and partition tools are part of Day 4.",
        }
        for name, description in descriptions.items():
            page = ctk.CTkFrame(self.page_host, fg_color=COLORS["surface"], corner_radius=18,
                                border_width=1, border_color=COLORS["border"])
            ctk.CTkLabel(
                page, text=name, text_color=COLORS["text"],
                font=get_font("display"),
            ).pack(anchor="w", padx=28, pady=(28, 8))
            ctk.CTkLabel(
                page, text=description, text_color=COLORS["muted"],
                font=get_font("body"), wraplength=540, justify="left",
            ).pack(anchor="w", padx=28)
            self.pages[name] = page

    def _nav_hover(self, button, entering):
        for label, btn in self.nav_buttons.items():
            if btn is not button:
                continue
            if label == self._current_page:
                return
            try:
                if entering:
                    btn.configure(fg_color=COLORS["blue_hover"])
                else:
                    btn.configure(fg_color=COLORS["sidebar"])
            except Exception:
                pass
    def _refresh_footer_status(self):
        # Same 85/75 thresholds as the Main-Plan detector contract.
        # Reads psutil directly so the footer works before Day3 detector lands.
        try:
            if self.winfo_exists():
                import psutil

                pct = float(psutil.virtual_memory().percent)
                try:
                    self.footer_card.set_sample(pct)
                    self.mascot.react(self.footer_card.state, pct)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self.after(2000, self._refresh_footer_status)
        except Exception:
            pass

    def _pulse_live(self):
        try:
            if self.winfo_exists() and hasattr(self, "live_dot"):
                self._live_phase = (self._live_phase + 1) % 2
                end = "#21866E" if self._live_phase == 0 else "#7AC9B5"
                start = "#7AC9B5" if self._live_phase == 0 else "#21866E"

                def _frame(t):
                    try:
                        self.live_dot.configure(
                            text_color=anim_h.hex_lerp(start, end, t)
                        )
                    except Exception:
                        pass

                anim_h.tween(self, 500, _frame, key="live")
        except Exception:
            pass
        try:
            self.after(1400, self._pulse_live)
        except Exception:
            pass

    def _animate_title(self):
        # Removed: per-frame font-size changes force a full pack relayout
        # every 16ms which is the biggest jank source. Title now swaps
        # instantly; smoothness comes from button color fades instead.
        return

    def _animate_host_slide(self):
        # Removed: per-frame grid padx changes relayout the whole page.
        return

    def _show_page(self, name):
        first = self._current_page is None
        self._current_page = name
        for page in self.pages.values():
            page.grid_forget()
        self.pages[name].grid(row=0, column=0, sticky="nsew")
        title, subtitle = PAGE_INFO[name]
        self.page_title.configure(text=title)
        self.page_subtitle.configure(text=subtitle)
        for label, button in self.nav_buttons.items():
            selected = label == name
            target_fg = COLORS["blue_soft"] if selected else COLORS["sidebar"]
            target_tx = COLORS["blue"] if selected else COLORS["muted"]
            try:
                start_fg = str(button.cget("fg_color"))
            except Exception:
                start_fg = target_fg

            def _make_frame(btn, s, e_fg, e_tx):
                def _frame(t):
                    try:
                        if s == target_fg:
                            btn.configure(fg_color=e_fg)
                        else:
                            try:
                                btn.configure(
                                    fg_color=anim_h.hex_lerp(s, e_fg, t)
                                )
                            except Exception:
                                btn.configure(fg_color=e_fg)
                        btn.configure(text_color=e_tx)
                    except Exception:
                        pass

                return _frame

            if selected:
                try:
                    button.configure(font=get_font("nav_active"))
                except Exception:
                    pass
            else:
                try:
                    button.configure(font=get_font("nav"))
                except Exception:
                    pass
            if anim_h.enabled() and not first:
                try:
                    anim_h.tween(
                        button,
                        ANIM.get("hover_ms", 90),
                        _make_frame(button, start_fg, target_fg, target_tx),
                        key=f"nav-{label}",
                    )
                except Exception:
                    button.configure(fg_color=target_fg, text_color=target_tx)
            else:
                button.configure(fg_color=target_fg, text_color=target_tx)
        if not first:
            self._animate_title()
            self._animate_host_slide()
