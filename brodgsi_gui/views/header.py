"""Header bar with title, breadcrumbs and monochrome settings button."""

import sys
import tkinter as tk

from ..theme import BwButton


class HeaderBar(tk.Frame):
    def __init__(self, parent, theme_mgr, i18n, on_settings_click, on_navigate_root):
        super().__init__(parent, highlightthickness=1)
        self.theme_mgr = theme_mgr
        self.i18n = i18n
        self.on_settings_click = on_settings_click
        self.on_navigate_root = on_navigate_root
        self.crumb_text = ""

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

    def _build_ui(self):
        # Left container
        self.left_box = tk.Frame(self)
        self.left_box.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=8)

        self.title_lbl = tk.Label(
            self.left_box,
            text="BRODGSI",
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 12, "bold"),
            cursor="hand2",
        )
        self.title_lbl.pack(side=tk.LEFT)
        self.title_lbl.bind("<Button-1>", lambda _: self.on_navigate_root())

        self.sep_lbl = tk.Label(
            self.left_box,
            text=" / ",
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 11),
        )
        self.sep_lbl.pack(side=tk.LEFT)

        self.crumb_lbl = tk.Label(
            self.left_box,
            text="",
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10),
        )
        self.crumb_lbl.pack(side=tk.LEFT)

        # Right container
        self.right_box = tk.Frame(self)
        self.right_box.pack(side=tk.RIGHT, fill=tk.Y, padx=12, pady=6)

        # Settings button with monochrome gear glyph
        self.btn_settings = BwButton(
            self.right_box,
            text=self.i18n.t("header_settings_btn"),
            command=self.on_settings_click,
            theme_mgr=self.theme_mgr,
            padx=10,
            pady=4,
        )
        self.btn_settings.pack(side=tk.RIGHT)

    def set_breadcrumb(self, text):
        self.crumb_text = text
        self.crumb_lbl.config(text=text)

    def apply_i18n(self):
        self.btn_settings.set_text(self.i18n.t("header_settings_btn"))

    def apply_theme(self, colors):
        bg = colors["surface"]
        fg = colors["fg"]
        fg_dim = colors["fg_dim"]
        border = colors["border"]

        self.config(bg=bg, highlightbackground=border, highlightcolor=border)
        self.left_box.config(bg=bg)
        self.right_box.config(bg=bg)
        self.title_lbl.config(bg=bg, fg=fg)
        self.sep_lbl.config(bg=bg, fg=fg_dim)
        self.crumb_lbl.config(bg=bg, fg=fg)
