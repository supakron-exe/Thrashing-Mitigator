import customtkinter as ctk

from ui.dashboard_tab import DashboardTab
from ui.theme import COLORS, apply_theme


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
        self.title("Thrashing Mitigator")
        self.geometry("920x680")
        self.minsize(900, 640)
        self.configure(fg_color=COLORS["background"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self._build_pages()
        self._show_page("Overview")

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=188, corner_radius=0, fg_color=COLORS["sidebar"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(3, weight=1)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(24, 22))
        ctk.CTkLabel(
            brand,
            text="TM",
            width=42,
            height=42,
            corner_radius=13,
            fg_color=COLORS["blue"],
            text_color="white",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(side="left")
        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            brand_text, text="Thrashing", text_color=COLORS["text"],
            font=ctk.CTkFont(size=15, weight="bold"), anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand_text, text="MITIGATOR", text_color=COLORS["muted"],
            font=ctk.CTkFont(size=9, weight="bold"), anchor="w",
        ).pack(anchor="w", pady=(1, 0))

        ctk.CTkLabel(
            sidebar, text="WORKSPACE", text_color=COLORS["muted"],
            font=ctk.CTkFont(size=10, weight="bold"), anchor="w",
        ).pack(fill="x", padx=22, pady=(0, 8))

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.pack(fill="x", padx=10)
        self.nav_buttons = {}
        for label, glyph in (
            ("Overview", "▦"),
            ("Thrashing", "◉"),
            ("Processes", "▤"),
            ("Simulator", "▥"),
            ("Paging + Partition", "▧"),
        ):
            button = ctk.CTkButton(
                nav,
                text=f"{glyph}   {label}",
                anchor="w",
                height=42,
                corner_radius=10,
                fg_color="transparent",
                hover_color=COLORS["blue_soft"],
                text_color=COLORS["muted"],
                font=ctk.CTkFont(size=13),
                command=lambda page=label: self._show_page(page),
            )
            button.pack(fill="x", pady=3)
            self.nav_buttons[label] = button

        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=20, pady=18)
        ctk.CTkFrame(footer, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            footer, text="OPERATING SYSTEMS  /  CHAPTER 3",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=9, weight="bold"),
            anchor="w", wraplength=170,
        ).pack(fill="x")
        ctk.CTkLabel(
            footer, text="Memory management demo",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=10), anchor="w",
        ).pack(fill="x", pady=(5, 0))

    def _build_main_area(self):
        main = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=12)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent", height=62)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)
        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")
        self.page_title = ctk.CTkLabel(
            title_block, text="Memory overview", text_color=COLORS["text"],
            font=ctk.CTkFont(size=22, weight="bold"), anchor="w",
        )
        self.page_title.pack(anchor="w")
        self.page_subtitle = ctk.CTkLabel(
            title_block, text="Live system memory and quick actions", text_color=COLORS["muted"],
            font=ctk.CTkFont(size=12), anchor="w",
        )
        self.page_subtitle.pack(anchor="w", pady=(2, 0))

        live = ctk.CTkFrame(
            header, fg_color="#E6F7F1", corner_radius=12,
            border_width=1, border_color="#D1EFE5",
        )
        live.grid(row=0, column=1, sticky="e", padx=(10, 0))
        ctk.CTkLabel(
            live, text="●  LIVE   ·   2 SEC", text_color="#21866E",
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(padx=12, pady=9)

        self.page_host = ctk.CTkFrame(main, fg_color="transparent")
        self.page_host.grid(row=1, column=0, sticky="nsew")
        self.page_host.grid_rowconfigure(0, weight=1)
        self.page_host.grid_columnconfigure(0, weight=1)

    def _build_pages(self):
        self.pages = {"Overview": DashboardTab(self.page_host)}
        self.pages["Overview"].grid(row=0, column=0, sticky="nsew")

        descriptions = {
            "Thrashing": "Live pressure monitoring and mitigation guidance will appear here.",
            "Processes": "The process list and memory controls are part of Day 2.",
            "Simulator": "FIFO, LRU, OPT, LFU, and MFU simulations are part of Day 3.",
            "Paging + Partition": "Address translation and partition tools are part of Day 4.",
        }
        for name, description in descriptions.items():
            page = ctk.CTkFrame(self.page_host, fg_color=COLORS["surface"], corner_radius=18)
            ctk.CTkLabel(
                page, text=name, text_color=COLORS["text"],
                font=ctk.CTkFont(size=20, weight="bold"),
            ).pack(anchor="w", padx=28, pady=(28, 8))
            ctk.CTkLabel(
                page, text=description, text_color=COLORS["muted"],
                font=ctk.CTkFont(size=13), wraplength=540, justify="left",
            ).pack(anchor="w", padx=28)
            self.pages[name] = page

    def _show_page(self, name):
        for page in self.pages.values():
            page.grid_forget()
        self.pages[name].grid(row=0, column=0, sticky="nsew")
        title, subtitle = PAGE_INFO[name]
        self.page_title.configure(text=title)
        self.page_subtitle.configure(text=subtitle)
        for label, button in self.nav_buttons.items():
            selected = label == name
            button.configure(
                fg_color=COLORS["blue_soft"] if selected else "transparent",
                text_color=COLORS["blue"] if selected else COLORS["muted"],
                font=ctk.CTkFont(size=13, weight="bold" if selected else "normal"),
            )
