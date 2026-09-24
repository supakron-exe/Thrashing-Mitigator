"""Topic-colored sidebar icons drawn with PIL (no emoji-font risk).

Each nav item gets its own shape + color so topics are recognizable
even before reading the label. Rendered large then downscaled for
smooth edges. Results are cached per process.
"""

from __future__ import annotations

from ui.theme import COLORS

_SIZE = 64          # draw large
_DISPLAY = 16       # shown size
_cache: dict[str, object] = {}

# label -> (shape, color-key)
NAV_ICONS = {
    "Overview": ("donut", "blue"),
    "Thrashing": ("warn", "red"),
    "Processes": ("list", "mint"),
    "Simulator": ("bars", "violet"),
    "Paging + Partition": ("grid", "orange"),
}


def _canvas():
    from PIL import Image

    return Image.new("RGBA", (_SIZE, _SIZE), (0, 0, 0, 0))


def _hex(rgb_key: str) -> tuple[int, int, int]:
    s = COLORS[rgb_key].lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _draw(shape: str, color: tuple[int, int, int]):
    from PIL import ImageDraw

    img = _canvas()
    d = ImageDraw.Draw(img)
    m = 10  # margin
    if shape == "donut":
        d.ellipse([m, m, _SIZE - m, _SIZE - m], outline=color + (255,), width=9)
        d.arc([m, m, _SIZE - m, _SIZE - m], start=300, end=60, fill=color + (255,), width=9)
    elif shape == "warn":
        d.polygon(
            [(_SIZE // 2, m), (_SIZE - m, _SIZE - m), (m, _SIZE - m)],
            outline=color + (255,),
        )
        # thick triangle via nested outlines
        d.polygon(
            [(_SIZE // 2, m + 7), (_SIZE - m - 6, _SIZE - m - 4), (m + 6, _SIZE - m - 4)],
            fill=color + (255,),
        )
        cx = _SIZE // 2
        d.rectangle([cx - 3, 28, cx + 3, 40], fill=(255, 255, 255, 255))
        d.ellipse([cx - 3, 43, cx + 3, 49], fill=(255, 255, 255, 255))
    elif shape == "list":
        for i, y in enumerate((16, 29, 42)):
            w = 40 if i != 2 else 28
            d.rounded_rectangle([12, y, 12 + w, y + 7], radius=3, fill=color + (255,))
    elif shape == "bars":
        bars = [(14, 40, 22, 50), (27, 30, 35, 50), (40, 18, 48, 50)]
        for x0, y0, x1, y1 in bars:
            d.rounded_rectangle([x0, y0, x1, y1], radius=3, fill=color + (255,))
    elif shape == "grid":
        cells = [(12, 12, 30, 30), (34, 12, 52, 30), (12, 34, 30, 52), (34, 34, 52, 52)]
        for i, (x0, y0, x1, y1) in enumerate(cells):
            if i == 0:
                d.rounded_rectangle([x0, y0, x1, y1], radius=5, fill=color + (255,))
            else:
                d.rounded_rectangle([x0, y0, x1, y1], radius=5, outline=color + (255,), width=5)
    else:  # fallback dot
        d.ellipse([m, m, _SIZE - m, _SIZE - m], fill=color + (255,))
    return img


def get_nav_icon(label: str):
    """Return a CTkImage for `label`, or None on any failure."""
    if label in _cache:
        return _cache[label]
    spec = NAV_ICONS.get(label)
    if spec is None:
        return None
    try:
        import customtkinter as ctk

        shape, color_key = spec
        img = _draw(shape, _hex(color_key))
        icon = ctk.CTkImage(light_image=img, dark_image=img, size=(_DISPLAY, _DISPLAY))
    except Exception:
        return None
    _cache[label] = icon
    return icon
