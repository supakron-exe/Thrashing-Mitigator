"""Tiny animation helpers for Tkinter/CustomTkinter.

`after()`-based, 60fps for cheap props (colors/text only).
Heavy work (matplotlib redraw, font-size/padx relayout) must NEVER
run per-frame — callers should animate cheap props per-frame and
redraw heavy canvases once at the end.
"""

from __future__ import annotations

from ui.theme import ANIM

_jobs: dict[int, str] = {}


def enabled() -> bool:
    return bool(ANIM.get("enabled", True))


def _frame_ms() -> int:
    fps = max(1, int(ANIM.get("fps", 60)))
    return max(10, 1000 // fps)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def _alive(widget) -> bool:
    try:
        return bool(widget.winfo_exists())
    except Exception:
        return False


def tween(widget, duration_ms: int, on_frame, on_done=None, key="default"):
    """Call `on_frame(eased_t)` over `duration_ms`, then `on_done()`.

    Same `key` on the same widget cancels the previous tween, so rapid
    refreshes never stack overlapping jobs (the main cause of jank).
    """
    if not enabled() or not _alive(widget):
        try:
            on_frame(1.0)
        except Exception:
            pass
        if on_done is not None:
            try:
                on_done()
            except Exception:
                pass
        return

    import time

    job_tag = (id(widget), key)
    run_id = object()
    _jobs[job_tag] = run_id
    start = time.monotonic()
    step = _frame_ms()
    # Fewer, evenly spaced frames: cheaper + smoother than 30 tiny ones
    # when each frame does real work.
    frames = max(2, min(24, int(round(duration_ms / step)) + 1))

    def _tick(i=0):
        if _jobs.get(job_tag) is not run_id or not _alive(widget):
            return
        t = min(1.0, i / max(1, frames - 1))
        try:
            on_frame(ease_out(t))
        except Exception:
            _jobs.pop(job_tag, None)
            return
        if t >= 1.0:
            _jobs.pop(job_tag, None)
            if on_done is not None:
                try:
                    on_done()
                except Exception:
                    pass
            return
        try:
            widget.after(step, lambda: _tick(i + 1))
        except Exception:
            _jobs.pop(job_tag, None)

    try:
        widget.after(0, lambda: _tick(0))
    except Exception:
        _jobs.pop(job_tag, None)


def stagger(widget, items, delay_ms: int, fn):
    """Run `fn(item)` with incremental delay for entrance effects."""
    if not enabled():
        for item in items:
            try:
                fn(item)
            except Exception:
                pass
        return
    for i, item in enumerate(items):
        try:
            widget.after(i * delay_ms, lambda it=item: fn(it))
        except Exception:
            pass


def count_up(widget, duration_ms: int, start: float, end: float, fmt, setter):
    """Animate a number from `start` to `end`, calling `setter(text)`."""
    if not enabled() or abs(end - start) < 1e-9:
        try:
            setter(fmt(end))
        except Exception:
            pass
        return

    # Skip tiny jitter: instant set is smoother than a 60fps micro-tween.
    span = abs(end - start)
    if span < 0.005:
        try:
            setter(fmt(end))
        except Exception:
            pass
        return

    def _frame(t):
        try:
            setter(fmt(lerp(start, end, t)))
        except Exception:
            pass

    tween(widget, min(duration_ms, 300), _frame, key="count")


def hex_lerp(c1: str, c2: str, t: float) -> str:
    def _ch(s):
        s = s.lstrip("#")
        return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))

    a, b = _ch(c1), _ch(c2)
    mixed = tuple(int(round(lerp(x, y, max(0.0, min(1.0, t))))) for x, y in zip(a, b))
    return "#%02X%02X%02X" % mixed
