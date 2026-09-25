"""Small, safe memory cleanup helpers used by the dashboard."""

from __future__ import annotations

import gc
import os

SUPPORTED_MODES = {"free", "standby", "defrag_sim"}


def optimize(mode: str = "free") -> float:
    """Attempt best-effort cleanup and return measured available MB delta."""
    mode = str(mode).lower().strip()
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"unknown optimization mode: {mode}")
    import psutil

    before = psutil.virtual_memory().available
    if os.name == "nt":
        try:
            import ctypes
            process = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.psapi.EmptyWorkingSet(process)
        except (AttributeError, OSError, PermissionError):
            pass
    gc.collect()
    after = psutil.virtual_memory().available
    return round(max(0.0, (after - before) / (1024 * 1024)), 1)
