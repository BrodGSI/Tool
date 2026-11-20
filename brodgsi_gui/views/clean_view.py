"""Disk cleanup view for BrodGSI GUI."""

import glob
import os
import shutil
import sys
import tkinter as tk
from tkinter import messagebox

import fsops

from ..theme import BwButton


def human_size(size: int) -> str:
    s = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if s < 1024:
            return f"{s:.1f} {unit}"
        s /= 1024
    return f"{s:.1f} PiB"


class CleanView(tk.Frame):
    def __init__(self, parent, theme_mgr, i18n, router):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.i18n = i18n
        self.router = router

        self.clean_tmp_var = tk.BooleanVar(value=True)
        self.clean_out_var = tk.BooleanVar(value=False)
        self.total_size = 0
        self.items_count = 0

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

    def _build_ui(self):
        f = tk.Frame(self, padx=30, pady=25)
        f.pack(fill=tk.BOTH, expand=True)

        self.title_lbl = tk.Label(
            f,
            text=self.i18n.t("clean_title"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 14, "bold"),
            anchor="w",
        )
        self.title_lbl.pack(fill=tk.X, pady=(0, 4))

        self.desc_lbl = tk.Label(
            f,
            text=self.i18n.t("clean_desc"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 9),
            anchor="w",
        )
        self.desc_lbl.pack(fill=tk.X, pady=(0, 20))

        # Scan result info box
        self.info_box = tk.Frame(f, highlightthickness=1, padx=15, pady=15)
        self.info_box.pack(fill=tk.X, pady=(0, 20))

        self.info_lbl = tk.Label(
            self.info_box,
            text=self.i18n.t("clean_scan"),
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 10),
            anchor="w",
        )
        self.info_lbl.pack(fill=tk.X)

        # Options
        self.chk_tmp = tk.Checkbutton(
            f,
            text=self.i18n.t("clean_opt_tmp"),
            variable=self.clean_tmp_var,
            command=self.scan_disk,
            anchor="w",
            cursor="hand2",
        )
        self.chk_tmp.pack(fill=tk.X, pady=4)

        self.chk_out = tk.Checkbutton(
            f,
            text=self.i18n.t("clean_opt_out"),
            variable=self.clean_out_var,
            command=self.scan_disk,
            anchor="w",
            cursor="hand2",
        )
        self.chk_out.pack(fill=tk.X, pady=4)

        # Buttons
        btn_row = tk.Frame(f)
        btn_row.pack(fill=tk.X, pady=(25, 0))

        self.btn_clean = BwButton(
            btn_row,
            text=self.i18n.t("btn_clean_now"),
            command=self._on_clean,
            primary=True,
            theme_mgr=self.theme_mgr,
            pady=10,
        )
        self.btn_clean.pack(side=tk.RIGHT, padx=(10, 0))

        self.btn_back = BwButton(
            btn_row,
            text=self.i18n.t("btn_back"),
            command=lambda: self.router.navigate("menu"),
            theme_mgr=self.theme_mgr,
            pady=8,
        )
        self.btn_back.pack(side=tk.LEFT)

        self.scan_disk()

    def _get_target_paths(self):
        dirs = []
        if self.clean_tmp_var.get():
            dirs.append("tmp")
        if self.clean_out_var.get():
            dirs.append("out")

        targets = []
        for d in dirs:
            targets.extend(glob.glob(os.path.join(d, "*")))
        return targets

    def scan_disk(self):
        targets = self._get_target_paths()
        self.items_count = len(targets)
        self.total_size = sum(fsops.disk_usage(t) for t in targets)
        size_str = human_size(self.total_size)
        text = self.i18n.t("clean_found", count=self.items_count, size=size_str)
        self.info_lbl.config(text=text)
        self.btn_clean.set_enabled(self.items_count > 0)

    def _on_clean(self):
        targets = self._get_target_paths()
        if not targets:
            return

        size_str = human_size(self.total_size)
        confirm = messagebox.askyesno(
            self.i18n.t("clean_confirm_title"),
            self.i18n.t("clean_confirm_msg", size=size_str),
        )
        if not confirm:
            return

        for entry in targets:
            try:
                if os.path.isdir(entry) and not os.path.islink(entry):
                    shutil.rmtree(entry, ignore_errors=True)
                else:
                    os.remove(entry)
            except Exception:
                pass

        messagebox.showinfo(
            self.i18n.t("app_title"),
            self.i18n.t("clean_done", size=size_str),
        )
        self.scan_disk()

    def apply_i18n(self):
        self.title_lbl.config(text=self.i18n.t("clean_title"))
        self.desc_lbl.config(text=self.i18n.t("clean_desc"))
        self.chk_tmp.config(text=self.i18n.t("clean_opt_tmp"))
        self.chk_out.config(text=self.i18n.t("clean_opt_out"))
        self.btn_clean.set_text(self.i18n.t("btn_clean_now"))
        self.btn_back.set_text(self.i18n.t("btn_back"))
        self.scan_disk()

    def apply_theme(self, colors):
        bg = colors["bg"]
        fg = colors["fg"]
        fg_dim = colors["fg_dim"]
        surf = colors["surface"]
        border = colors["border"]

        self.config(bg=bg)
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.config(bg=bg)

        self.title_lbl.config(bg=bg, fg=fg)
        self.desc_lbl.config(bg=bg, fg=fg_dim)
        self.info_box.config(bg=surf, highlightbackground=border, highlightcolor=border)
        self.info_lbl.config(bg=surf, fg=fg)

        for chk in (self.chk_tmp, self.chk_out):
            chk.config(
                bg=bg,
                fg=fg,
                activebackground=bg,
                activeforeground=fg,
                selectcolor=surf,
                highlightbackground=bg,
            )
