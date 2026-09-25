import tkinter as tk
from tkinter import ttk

import customtkinter as ctk
import psutil

from ui.theme import COLORS, get_font


class ProcessTab(ctk.CTkFrame):
    """Top memory-consuming processes with guarded controls."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._processes = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkButton(toolbar, text="Refresh", width=110, height=34, fg_color=COLORS["blue"],
                      hover_color=COLORS["blue_hover"], font=get_font("body_bold"), command=self.refresh).pack(side="left")
        ctk.CTkButton(toolbar, text="Kill selected", width=120, height=34, fg_color=COLORS["red"],
                      hover_color="#C94343", font=get_font("body_bold"), command=self.kill_selected).pack(side="left", padx=(8, 0))
        ctk.CTkButton(toolbar, text="Suspend selected", width=140, height=34, fg_color=COLORS["amber"],
                      hover_color="#C9830D", font=get_font("body_bold"), command=self.suspend_selected).pack(side="left", padx=(8, 0))
        self.status_var = tk.StringVar(value="Loading processes...")
        ctk.CTkLabel(toolbar, textvariable=self.status_var, text_color=COLORS["muted"],
                     font=get_font("hint")).pack(side="right")

        card = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=16,
                            border_width=1, border_color=COLORS["border_strong"])
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)
        style = ttk.Style()
        try:
            style.configure("Day2.Treeview", rowheight=30, font=("Segoe UI", 10),
                            background=COLORS["surface"], fieldbackground=COLORS["surface"], foreground=COLORS["text"])
            style.configure("Day2.Treeview.Heading", font=("Segoe UI", 10, "bold"))
        except tk.TclError:
            pass
        self.tree = ttk.Treeview(card, columns=("pid", "name", "memory"), show="headings",
                                 style="Day2.Treeview", selectmode="browse")
        self.tree.heading("pid", text="PID")
        self.tree.heading("name", text="Name")
        self.tree.heading("memory", text="Memory (MB)")
        self.tree.column("pid", width=100, anchor="center", stretch=False)
        self.tree.column("name", width=300, anchor="w")
        self.tree.column("memory", width=150, anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)
        self.tree.configure(yscrollcommand=scrollbar.set)

    def refresh(self):
        rows = []
        for process in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                info = process.info
                rss = info["memory_info"].rss if info["memory_info"] else 0
                rows.append((float(rss), int(info["pid"]), info.get("name") or "(unknown)"))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
                continue
        rows.sort(reverse=True)
        top = rows[:10]
        self._processes = {}
        for _, pid, _ in top:
            try:
                self._processes[str(pid)] = psutil.Process(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        for item in self.tree.get_children():
            self.tree.delete(item)
        for rss, pid, name in top:
            self.tree.insert("", "end", iid=str(pid), values=(pid, name, f"{rss / (1024 ** 2):.1f}"))
        self.status_var.set(f"Showing {len(top)} processes sorted by memory")

    def _selected_process(self):
        selected = self.tree.selection()
        if not selected:
            self.status_var.set("Select a process first")
            return None
        process = self._processes.get(selected[0])
        if process is None:
            self.status_var.set("Refresh the list before controlling this process")
        return process

    def kill_selected(self):
        process = self._selected_process()
        if process is None:
            return
        try:
            process.kill()
            self.status_var.set(f"Sent kill request to PID {process.pid}")
            self.after(350, self.refresh)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as exc:
            self.status_var.set(f"Could not kill PID {process.pid}: {exc.__class__.__name__}")

    def suspend_selected(self):
        process = self._selected_process()
        if process is None:
            return
        try:
            process.suspend()
            self.status_var.set(f"Suspended PID {process.pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as exc:
            self.status_var.set(f"Could not suspend PID {process.pid}: {exc.__class__.__name__}")
