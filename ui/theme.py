import customtkinter as ctk


COLORS = {
    # Layer 0-2: depth system (background < inset < surface < overlay)
    "background": "#F3F5FB",
    "surface": "#FFFFFF",
    "surface_2": "#EFF3FA",
    "overlay": "#FFFFFF",
    "sidebar": "#FFFFFF",
    "sidebar_bottom": "#EFF3FA",
    "text": "#172033",
    "muted": "#718096",
    "border": "#E5EAF2",
    "border_strong": "#D3DBE8",
    "blue": "#1677E8",
    "blue_soft": "#EAF3FF",
    "blue_hover": "#D8E9FF",
    "pink": "#E852A5",
    "pink_soft": "#FDE7F3",
    "mint": "#4DBFA9",
    "mint_soft": "#E6F7F1",
    "mint_border": "#D1EFE5",
    "amber": "#E8A013",
    "amber_soft": "#FFF4DE",
    "violet": "#7C5CFF",
    "violet_soft": "#EEEAFF",
    "orange": "#E88213",
    "orange_soft": "#FFF0E0",
    "red": "#E45757",
    "red_soft": "#FDECEC",
}

# Modern clean, English-only: Segoe UI everywhere (built into Windows).
FONT_FAMILY = "Segoe UI"

FONTS = {
    "display": {"size": 24, "weight": "bold"},
    "title": {"size": 16, "weight": "bold"},
    "subtitle": {"size": 12, "weight": "normal"},
    "body": {"size": 13, "weight": "normal"},
    "body_bold": {"size": 13, "weight": "bold"},
    "nav": {"size": 13, "weight": "normal"},
    "nav_active": {"size": 13, "weight": "bold"},
    "metric_value": {"size": 20, "weight": "bold"},
    "metric_hint": {"size": 11, "weight": "bold"},
    "caption": {"size": 9, "weight": "bold"},
    "hint": {"size": 9, "weight": "normal"},
    "tiny": {"size": 8, "weight": "normal"},
}

ANIM = {
    "enabled": True,
    "fps": 60,
    "page_ms": 120,
    "hover_ms": 90,
    "count_ms": 300,
    "sweep_ms": 350,
}


def get_font(role="body"):
    spec = FONTS.get(role, FONTS["body"])
    try:
        return ctk.CTkFont(
            family=FONT_FAMILY, size=spec["size"], weight=spec["weight"]
        )
    except Exception:
        return ctk.CTkFont(size=spec["size"], weight=spec["weight"])


def apply_theme():
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    try:
        from matplotlib import rcParams

        rcParams["font.family"] = FONT_FAMILY
        rcParams["font.size"] = 8.5
        rcParams["axes.unicode_minus"] = False
    except Exception:
        pass
