import customtkinter as ctk


COLORS = {
    "background": "#F3F5FB",
    "surface": "#FFFFFF",
    "sidebar": "#FFFFFF",
    "text": "#172033",
    "muted": "#718096",
    "border": "#E5EAF2",
    "blue": "#1677E8",
    "blue_soft": "#EAF3FF",
    "pink": "#E852A5",
    "mint": "#4DBFA9",
    "red": "#E45757",
}


def apply_theme():
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
