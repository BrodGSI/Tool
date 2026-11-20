"""Main menu and submenus for BrodGSI GUI."""

import sys
import tkinter as tk

from ..theme import BwButton


class MainMenuView(tk.Frame):
    """Primary navigation menu."""

    def __init__(self, parent, theme_mgr, i18n, router):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.i18n = i18n
        self.router = router

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

    def _build_ui(self):
        self.box = tk.Frame(self, padx=40, pady=30)
        self.box.pack(fill=tk.BOTH, expand=True)

        self.title_lbl = tk.Label(
            self.box,
            text=self.i18n.t("menu_title"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 16, "bold"),
            anchor="w",
        )
        self.title_lbl.pack(fill=tk.X, pady=(0, 4))

        self.desc_lbl = tk.Label(
            self.box,
            text=self.i18n.t("menu_desc"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10),
            anchor="w",
        )
        self.desc_lbl.pack(fill=tk.X, pady=(0, 25))

        # Menu buttons
        self.btn_build = BwButton(
            self.box,
            text=self.i18n.t("btn_build_menu"),
            command=lambda: self.router.navigate("build_menu"),
            theme_mgr=self.theme_mgr,
            pady=10,
        )
        self.btn_build.pack(fill=tk.X, pady=6)

        self.btn_rebuild = BwButton(
            self.box,
            text=self.i18n.t("btn_rebuild_menu"),
            command=lambda: self.router.navigate("rebuild"),
            theme_mgr=self.theme_mgr,
            pady=10,
        )
        self.btn_rebuild.pack(fill=tk.X, pady=6)

        self.btn_list = BwButton(
            self.box,
            text=self.i18n.t("btn_list_menu"),
            command=lambda: self.router.navigate("list"),
            theme_mgr=self.theme_mgr,
            pady=10,
        )
        self.btn_list.pack(fill=tk.X, pady=6)

        self.btn_clean = BwButton(
            self.box,
            text=self.i18n.t("btn_clean_menu"),
            command=lambda: self.router.navigate("clean"),
            theme_mgr=self.theme_mgr,
            pady=10,
        )
        self.btn_clean.pack(fill=tk.X, pady=6)

        self.btn_exit = BwButton(
            self.box,
            text=self.i18n.t("btn_exit"),
            command=lambda: self.winfo_toplevel().destroy(),
            theme_mgr=self.theme_mgr,
            pady=8,
        )
        self.btn_exit.pack(fill=tk.X, pady=(20, 6))

    def apply_i18n(self):
        self.title_lbl.config(text=self.i18n.t("menu_title"))
        self.desc_lbl.config(text=self.i18n.t("menu_desc"))
        self.btn_build.set_text(self.i18n.t("btn_build_menu"))
        self.btn_rebuild.set_text(self.i18n.t("btn_rebuild_menu"))
        self.btn_list.set_text(self.i18n.t("btn_list_menu"))
        self.btn_clean.set_text(self.i18n.t("btn_clean_menu"))
        self.btn_exit.set_text(self.i18n.t("btn_exit"))

    def apply_theme(self, colors):
        bg = colors["bg"]
        fg = colors["fg"]
        fg_dim = colors["fg_dim"]

        self.config(bg=bg)
        self.box.config(bg=bg)
        self.title_lbl.config(bg=bg, fg=fg)
        self.desc_lbl.config(bg=bg, fg=fg_dim)


class BuildSubmenuView(tk.Frame):
    """Submenu for GSI build options (from file or URL)."""

    def __init__(self, parent, theme_mgr, i18n, router):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.i18n = i18n
        self.router = router

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

    def _build_ui(self):
        self.box = tk.Frame(self, padx=40, pady=30)
        self.box.pack(fill=tk.BOTH, expand=True)

        self.title_lbl = tk.Label(
            self.box,
            text=self.i18n.t("build_sub_title"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 16, "bold"),
            anchor="w",
        )
        self.title_lbl.pack(fill=tk.X, pady=(0, 4))

        self.desc_lbl = tk.Label(
            self.box,
            text=self.i18n.t("build_sub_desc"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10),
            anchor="w",
        )
        self.desc_lbl.pack(fill=tk.X, pady=(0, 25))

        # Option 1: File
        self.btn_file = BwButton(
            self.box,
            text=self.i18n.t("btn_build_from_file"),
            command=lambda: self.router.navigate("build_file"),
            theme_mgr=self.theme_mgr,
            pady=12,
        )
        self.btn_file.pack(fill=tk.X, pady=6)

        self.desc_file = tk.Label(
            self.box,
            text=self.i18n.t("btn_build_from_file_desc"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 9),
            anchor="w",
            wraplength=520,
            justify=tk.LEFT,
        )
        self.desc_file.pack(fill=tk.X, padx=8, pady=(0, 15))

        # Option 2: URL
        self.btn_url = BwButton(
            self.box,
            text=self.i18n.t("btn_build_from_url"),
            command=lambda: self.router.navigate("build_url"),
            theme_mgr=self.theme_mgr,
            pady=12,
        )
        self.btn_url.pack(fill=tk.X, pady=6)

        self.desc_url = tk.Label(
            self.box,
            text=self.i18n.t("btn_build_from_url_desc"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 9),
            anchor="w",
            wraplength=520,
            justify=tk.LEFT,
        )
        self.desc_url.pack(fill=tk.X, padx=8, pady=(0, 25))

        # Back
        self.btn_back = BwButton(
            self.box,
            text=self.i18n.t("btn_back_to_menu"),
            command=lambda: self.router.navigate("menu"),
            theme_mgr=self.theme_mgr,
            pady=8,
        )
        self.btn_back.pack(fill=tk.X, pady=(10, 6))

    def apply_i18n(self):
        self.title_lbl.config(text=self.i18n.t("build_sub_title"))
        self.desc_lbl.config(text=self.i18n.t("build_sub_desc"))
        self.btn_file.set_text(self.i18n.t("btn_build_from_file"))
        self.desc_file.config(text=self.i18n.t("btn_build_from_file_desc"))
        self.btn_url.set_text(self.i18n.t("btn_build_from_url"))
        self.desc_url.config(text=self.i18n.t("btn_build_from_url_desc"))
        self.btn_back.set_text(self.i18n.t("btn_back_to_menu"))

    def apply_theme(self, colors):
        bg = colors["bg"]
        fg = colors["fg"]
        fg_dim = colors["fg_dim"]

        self.config(bg=bg)
        self.box.config(bg=bg)
        self.title_lbl.config(bg=bg, fg=fg)
        self.desc_lbl.config(bg=bg, fg=fg_dim)
        self.desc_file.config(bg=bg, fg=fg_dim)
        self.desc_url.config(bg=bg, fg=fg_dim)
