"""Rebuild view for BrodGSI GUI."""

import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk

from ..theme import BwButton, colorize_tree

GSILIST_PATH = "tmp/gsilist.json"


def get_available_build_names():
    try:
        if os.path.exists(GSILIST_PATH):
            with open(GSILIST_PATH, "r", encoding="utf-8") as f:
                entries = json.load(f)
                names = [e.get("rom_name") for e in entries if e.get("rom_name")]
                return list(dict.fromkeys(reversed(names)))
    except Exception:
        pass
    return []


class RebuildView(tk.Frame):
    def __init__(self, parent, theme_mgr, i18n, router, settings):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.i18n = i18n
        self.router = router
        self.settings = settings

        self.name_var = tk.StringVar()
        self.compress_var = tk.BooleanVar(value=False)
        self.avb_key_var = tk.StringVar()

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

    def _build_ui(self):
        f = tk.Frame(self, padx=30, pady=25)
        f.pack(fill=tk.BOTH, expand=True)

        self.title_lbl = tk.Label(
            f,
            text=self.i18n.t("rebuild_title"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 14, "bold"),
            anchor="w",
        )
        self.title_lbl.pack(fill=tk.X, pady=(0, 4))

        self.desc_lbl = tk.Label(
            f,
            text=self.i18n.t("rebuild_desc"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 9),
            anchor="w",
            wraplength=520,
            justify=tk.LEFT,
        )
        self.desc_lbl.pack(fill=tk.X, pady=(0, 20))

        # Selection of build
        self.lbl_select = tk.Label(
            f,
            text=self.i18n.t("rebuild_select"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.lbl_select.pack(fill=tk.X, pady=(0, 4))

        self.cb_names = ttk.Combobox(
            f,
            textvariable=self.name_var,
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 10),
        )
        self.cb_names.pack(fill=tk.X, ipady=4, pady=(0, 15))

        # AVB key
        self.lbl_avb = tk.Label(
            f,
            text=self.i18n.t("field_avb_key"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.lbl_avb.pack(fill=tk.X, pady=(0, 2))

        avb_row = tk.Frame(f)
        avb_row.pack(fill=tk.X, pady=(0, 15))

        self.ent_avb = tk.Entry(
            avb_row,
            textvariable=self.avb_key_var,
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 10),
            relief="solid",
            bd=1,
        )
        self.ent_avb.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        self.btn_avb_browse = BwButton(
            avb_row,
            text=self.i18n.t("field_browse"),
            command=self._on_browse_avb,
            theme_mgr=self.theme_mgr,
            padx=8,
            pady=2,
        )
        self.btn_avb_browse.pack(side=tk.RIGHT, padx=(8, 0))

        # Options
        self.chk_compress = tk.Checkbutton(
            f,
            text=self.i18n.t("opt_compress"),
            variable=self.compress_var,
            anchor="w",
            cursor="hand2",
        )
        self.chk_compress.pack(fill=tk.X, pady=(0, 25))

        # Buttons
        btn_row = tk.Frame(f)
        btn_row.pack(fill=tk.X, pady=(10, 0))

        self.btn_start = BwButton(
            btn_row,
            text=self.i18n.t("btn_start_rebuild"),
            command=self._on_start,
            primary=True,
            theme_mgr=self.theme_mgr,
            pady=10,
        )
        self.btn_start.pack(side=tk.RIGHT, padx=(10, 0))

        self.btn_back = BwButton(
            btn_row,
            text=self.i18n.t("btn_back"),
            command=lambda: self.router.navigate("menu"),
            theme_mgr=self.theme_mgr,
            pady=8,
        )
        self.btn_back.pack(side=tk.LEFT)

        self.refresh_names()

    def refresh_names(self):
        names = get_available_build_names()
        self.cb_names["values"] = names
        if names and not self.name_var.get():
            self.name_var.set(names[0])

    def _on_browse_avb(self):
        chosen = filedialog.askopenfilename(filetypes=[("RSA Key", "*.pem;*.key"), ("All files", "*.*")])
        if chosen:
            self.avb_key_var.set(chosen)

    def _on_start(self):
        name = self.name_var.get().strip()
        if not name:
            from tkinter import messagebox

            messagebox.showwarning(self.i18n.t("app_title"), self.i18n.t("error_name_empty"))
            return

        rebuild_args = {
            "name": name,
            "compress": self.compress_var.get(),
            "avb_key": self.avb_key_var.get().strip() or None,
        }
        self.router.start_rebuild(rebuild_args)

    def apply_i18n(self):
        self.title_lbl.config(text=self.i18n.t("rebuild_title"))
        self.desc_lbl.config(text=self.i18n.t("rebuild_desc"))
        self.lbl_select.config(text=self.i18n.t("rebuild_select"))
        self.lbl_avb.config(text=self.i18n.t("field_avb_key"))
        self.btn_avb_browse.set_text(self.i18n.t("field_browse"))
        self.chk_compress.config(text=self.i18n.t("opt_compress"))
        self.btn_start.set_text(self.i18n.t("btn_start_rebuild"))
        self.btn_back.set_text(self.i18n.t("btn_back"))

    def apply_theme(self, colors):
        bg = colors["bg"]
        fg = colors["fg"]
        fg_dim = colors["fg_dim"]
        surf = colors["surface"]
        border = colors["border"]
        entry_bg = colors["entry_bg"]
        entry_fg = colors["entry_fg"]

        colorize_tree(self, bg)
        self.config(bg=bg)

        self.title_lbl.config(bg=bg, fg=fg)
        self.desc_lbl.config(bg=bg, fg=fg_dim)
        self.lbl_select.config(bg=bg, fg=fg)
        self.lbl_avb.config(bg=bg, fg=fg)

        self.ent_avb.config(
            bg=entry_bg,
            fg=entry_fg,
            insertbackground=entry_fg,
            highlightthickness=1,
            highlightbackground=border,
            highlightcolor=colors["border_focus"],
        )

        self.chk_compress.config(
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            selectcolor=surf,
            highlightbackground=bg,
        )
