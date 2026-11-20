"""Settings modal dialog for BrodGSI GUI."""

import shutil
import sys
import tkinter as tk

from tools.host.env import REQUIRED_TOOLS, find_tool

from .theme import BwButton


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, theme_mgr, i18n, settings_storage):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.i18n = i18n
        self.settings = settings_storage

        self.title(self.i18n.t("settings_title"))
        self.geometry("480x460")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.lang_var = tk.StringVar(value=self.settings.language)
        self.theme_var = tk.StringVar(value=self.settings.theme)

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

        # Center on parent
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        x = max(0, px + (pw - w) // 2)
        y = max(0, py + (ph - h) // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        self.container = tk.Frame(self, padx=20, pady=20)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.title_lbl = tk.Label(
            self.container,
            text=self.i18n.t("settings_title"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 14, "bold"),
            anchor="w",
        )
        self.title_lbl.pack(fill=tk.X, pady=(0, 15))

        # Language selection
        self.lang_lbl = tk.Label(
            self.container,
            text=self.i18n.t("settings_lang_label"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.lang_lbl.pack(fill=tk.X, pady=(5, 3))

        self.lang_radios = []
        for val, key in (
            ("system", "settings_lang_system"),
            ("ru", "settings_lang_ru"),
            ("en", "settings_lang_en"),
        ):
            text = self.i18n.t(key, lang=self.i18n.get_active_lang().upper())
            rb = tk.Radiobutton(
                self.container,
                text=text,
                variable=self.lang_var,
                value=val,
                command=self._on_lang_changed,
                anchor="w",
                padx=10,
                pady=2,
                cursor="hand2",
            )
            rb.pack(fill=tk.X)
            self.lang_radios.append((rb, val, key))

        # Theme selection
        self.theme_lbl = tk.Label(
            self.container,
            text=self.i18n.t("settings_theme_label"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.theme_lbl.pack(fill=tk.X, pady=(15, 3))

        self.theme_radios = []
        for val, key in (
            ("neon", "settings_theme_neon"),
            ("dark", "settings_theme_dark"),
            ("light", "settings_theme_light"),
            ("system", "settings_theme_system"),
        ):
            text = self.i18n.t(key)
            rb = tk.Radiobutton(
                self.container,
                text=text,
                variable=self.theme_var,
                value=val,
                command=self._on_theme_changed,
                anchor="w",
                padx=10,
                pady=2,
                cursor="hand2",
            )
            rb.pack(fill=tk.X)
            self.theme_radios.append((rb, val, key))

        # Tools status
        self.tools_box = tk.LabelFrame(
            self.container,
            text=f" {self.i18n.t('settings_tools_status')} ",
            padx=10,
            pady=8,
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 9, "bold"),
        )
        self.tools_box.pack(fill=tk.X, pady=(15, 15))

        tools_list = list(REQUIRED_TOOLS) + ["aria2c", "mkfs.erofs"]
        self.tool_labels = []
        for t in tools_list:
            found = bool(find_tool(t) or shutil.which(t))
            status_txt = self.i18n.t("settings_status_ok") if found else self.i18n.t("settings_status_missing")
            lbl = tk.Label(
                self.tools_box,
                text=f"{t:<14} : {status_txt}",
                font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 9),
                anchor="w",
            )
            lbl.pack(fill=tk.X, pady=1)
            self.tool_labels.append(lbl)

        # Close button
        self.btn_save = BwButton(
            self.container,
            text=self.i18n.t("btn_save_close"),
            command=self._on_save,
            primary=True,
            theme_mgr=self.theme_mgr,
        )
        self.btn_save.pack(anchor="e", pady=(5, 0))

    def _on_lang_changed(self):
        new_lang = self.lang_var.get()
        self.i18n.set_lang(new_lang)
        self.settings.language = new_lang
        self.settings.save()

    def _on_theme_changed(self):
        new_theme = self.theme_var.get()
        self.theme_mgr.set_preference(new_theme)
        self.settings.theme = new_theme
        self.settings.save()

    def apply_i18n(self):
        self.title(self.i18n.t("settings_title"))
        self.title_lbl.config(text=self.i18n.t("settings_title"))
        self.lang_lbl.config(text=self.i18n.t("settings_lang_label"))
        for rb, val, key in self.lang_radios:
            rb.config(text=self.i18n.t(key, lang=self.i18n.get_active_lang().upper()))

        self.theme_lbl.config(text=self.i18n.t("settings_theme_label"))
        for rb, val, key in self.theme_radios:
            rb.config(text=self.i18n.t(key))

        self.tools_box.config(text=f" {self.i18n.t('settings_tools_status')} ")
        self.btn_save.set_text(self.i18n.t("btn_save_close"))

    def apply_theme(self, colors):
        bg = colors["bg"]
        fg = colors["fg"]
        surf = colors["surface"]
        border = colors["border"]

        self.config(bg=bg)
        self.container.config(bg=bg)
        self.title_lbl.config(bg=bg, fg=fg)
        self.lang_lbl.config(bg=bg, fg=fg)
        self.theme_lbl.config(bg=bg, fg=fg)

        for rb, _, _ in self.lang_radios:
            rb.config(
                bg=bg,
                fg=fg,
                activebackground=bg,
                activeforeground=fg,
                selectcolor=surf,
                highlightbackground=bg,
            )

        for rb, _, _ in self.theme_radios:
            rb.config(
                bg=bg,
                fg=fg,
                activebackground=bg,
                activeforeground=fg,
                selectcolor=surf,
                highlightbackground=bg,
            )

        self.tools_box.config(
            bg=surf,
            fg=fg,
            highlightbackground=border,
            highlightthickness=1,
            bd=0,
        )
        for lbl in self.tool_labels:
            lbl.config(bg=surf, fg=fg)

    def _on_save(self):
        self.theme_mgr.remove_listener(self.apply_theme)
        self.i18n.remove_listener(self.apply_i18n)
        self.destroy()
