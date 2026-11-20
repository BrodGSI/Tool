"""Build history and images list view for BrodGSI GUI."""

import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

from ..theme import BwButton, colorize_tree

GSILIST_PATH = "tmp/gsilist.json"


def open_system_folder(path: str):
    """Opens directory in file explorer across platforms."""
    folder = path if os.path.isdir(path) else os.path.dirname(path)
    if not os.path.exists(folder):
        return
    try:
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder], check=False)
        else:
            subprocess.run(["xdg-open", folder], check=False)
    except Exception:
        pass


class ListView(tk.Frame):
    def __init__(self, parent, theme_mgr, i18n, router):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.i18n = i18n
        self.router = router
        self.entries = []

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

    def _build_ui(self):
        f = tk.Frame(self, padx=30, pady=20)
        f.pack(fill=tk.BOTH, expand=True)

        self.title_lbl = tk.Label(
            f,
            text=self.i18n.t("list_title"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 14, "bold"),
            anchor="w",
        )
        self.title_lbl.pack(fill=tk.X, pady=(0, 4))

        self.desc_lbl = tk.Label(
            f,
            text=self.i18n.t("list_desc"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 9),
            anchor="w",
        )
        self.desc_lbl.pack(fill=tk.X, pady=(0, 15))

        # Treeview
        tree_frame = tk.Frame(f)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        columns = ("id", "name", "status", "images")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("id", text=self.i18n.t("list_col_id"))
        self.tree.heading("name", text=self.i18n.t("list_col_name"))
        self.tree.heading("status", text=self.i18n.t("list_col_status"))
        self.tree.heading("images", text=self.i18n.t("list_col_images"))

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("images", width=340, anchor="w")

        scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Button toolbar
        btn_row = tk.Frame(f)
        btn_row.pack(fill=tk.X)

        self.btn_back = BwButton(
            btn_row,
            text=self.i18n.t("btn_back"),
            command=lambda: self.router.navigate("menu"),
            theme_mgr=self.theme_mgr,
            pady=6,
        )
        self.btn_back.pack(side=tk.LEFT)

        self.btn_refresh = BwButton(
            btn_row,
            text=self.i18n.t("btn_refresh"),
            command=self.load_entries,
            theme_mgr=self.theme_mgr,
            pady=6,
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=10)

        self.btn_rebuild = BwButton(
            btn_row,
            text=self.i18n.t("btn_rebuild_this"),
            command=self._on_rebuild_selected,
            primary=True,
            theme_mgr=self.theme_mgr,
            pady=6,
        )
        self.btn_rebuild.pack(side=tk.RIGHT)

        self.btn_open = BwButton(
            btn_row,
            text=self.i18n.t("btn_open_folder"),
            command=self._on_open_selected,
            theme_mgr=self.theme_mgr,
            pady=6,
        )
        self.btn_open.pack(side=tk.RIGHT, padx=10)

        self.load_entries()

    def load_entries(self):
        self.tree.delete(*self.tree.get_children())
        self.entries = []
        try:
            if os.path.exists(GSILIST_PATH):
                with open(GSILIST_PATH, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
        except Exception:
            self.entries = []

        if not self.entries:
            return

        for i, entry in enumerate(self.entries):
            images = entry.get("output_images") or {
                "system": f"{entry.get('output_path', '')}.img"
            }
            img_list = list(images.values())
            exists = all(os.path.exists(p) for p in img_list) if img_list else False
            status_txt = self.i18n.t("list_status_exists") if exists else self.i18n.t("list_status_missing")
            images_str = ", ".join(os.path.basename(p) for p in img_list)

            self.tree.insert(
                "",
                "end",
                iid=str(i),
                values=(i + 1, entry.get("output_name", entry.get("rom_name", "?")), status_txt, images_str),
            )

    def _get_selected_entry(self):
        sel = self.tree.selection()
        if not sel:
            return None
        idx = int(sel[0])
        if 0 <= idx < len(self.entries):
            return self.entries[idx]
        return None

    def _on_open_selected(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        out_path = entry.get("output_path") or entry.get("output")
        if out_path:
            open_system_folder(os.path.dirname(out_path))
        elif os.path.isdir("out"):
            open_system_folder("out")

    def _on_rebuild_selected(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        rom_name = entry.get("rom_name")
        self.router.navigate("rebuild", initial_name=rom_name)

    def apply_i18n(self):
        self.title_lbl.config(text=self.i18n.t("list_title"))
        self.desc_lbl.config(text=self.i18n.t("list_desc"))
        self.tree.heading("id", text=self.i18n.t("list_col_id"))
        self.tree.heading("name", text=self.i18n.t("list_col_name"))
        self.tree.heading("status", text=self.i18n.t("list_col_status"))
        self.tree.heading("images", text=self.i18n.t("list_col_images"))
        self.btn_back.set_text(self.i18n.t("btn_back"))
        self.btn_refresh.set_text(self.i18n.t("btn_refresh"))
        self.btn_open.set_text(self.i18n.t("btn_open_folder"))
        self.btn_rebuild.set_text(self.i18n.t("btn_rebuild_this"))
        self.load_entries()

    def apply_theme(self, colors):
        bg = colors["bg"]
        fg = colors["fg"]
        fg_dim = colors["fg_dim"]
        surf = colors["surface"]
        border = colors["border"]

        colorize_tree(self, bg)
        self.config(bg=bg)

        self.title_lbl.config(bg=bg, fg=fg)
        self.desc_lbl.config(bg=bg, fg=fg_dim)

        # Style treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=surf,
            foreground=fg,
            fieldbackground=surf,
            bordercolor=border,
            darkcolor=border,
            lightcolor=border,
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 9),
            rowheight=24,
        )
        style.map(
            "Treeview",
            background=[("selected", colors["select_bg"])],
            foreground=[("selected", colors["select_fg"])],
        )
        style.configure(
            "Treeview.Heading",
            background=colors["btn_bg"],
            foreground=colors["btn_fg"],
            bordercolor=border,
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 9, "bold"),
        )
