"""Build execution and real-time log view for BrodGSI GUI."""

import os
import subprocess
import sys
import tkinter as tk

from ..theme import BwButton, BwProgressBar, colorize_tree


def open_system_folder(path: str):
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


class LogView(tk.Frame):
    def __init__(self, parent, theme_mgr, i18n, router):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.i18n = i18n
        self.router = router

        self.current_state_key = "state_idle"
        self.output_directory = None
        self.is_running = False

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

    def _build_ui(self):
        f = tk.Frame(self, padx=25, pady=20)
        f.pack(fill=tk.BOTH, expand=True)

        # Header status row
        status_box = tk.Frame(f)
        status_box.pack(fill=tk.X, pady=(0, 10))

        self.lbl_title = tk.Label(
            status_box,
            text=self.i18n.t("log_title"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 13, "bold"),
            anchor="w",
        )
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_pct = tk.Label(
            status_box,
            text="0%",
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 12, "bold"),
            anchor="e",
        )
        self.lbl_pct.pack(side=tk.RIGHT)

        # Progress bar
        self.pbar = BwProgressBar(f, height=12, theme_mgr=self.theme_mgr)
        self.pbar.pack(fill=tk.X, pady=(0, 8))

        # State text
        self.lbl_state = tk.Label(
            f,
            text=f"{self.i18n.t('log_state_label')} {self.i18n.t('state_idle')}",
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 9),
            anchor="w",
        )
        self.lbl_state.pack(fill=tk.X, pady=(0, 8))

        # Text Console Box
        txt_frame = tk.Frame(f)
        txt_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.txt_log = tk.Text(
            txt_frame,
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 9),
            wrap="none",
            relief="solid",
            bd=1,
            padx=8,
            pady=8,
        )
        scroll_y = tk.Scrollbar(txt_frame, orient="vertical", command=self.txt_log.yview)
        scroll_x = tk.Scrollbar(txt_frame, orient="horizontal", command=self.txt_log.xview)
        self.txt_log.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Control buttons
        btn_row = tk.Frame(f)
        btn_row.pack(fill=tk.X)

        self.btn_back = BwButton(
            btn_row,
            text=self.i18n.t("btn_back_to_menu"),
            command=lambda: self.router.navigate("menu"),
            theme_mgr=self.theme_mgr,
            pady=6,
        )
        self.btn_back.pack(side=tk.LEFT)

        self.btn_stop = BwButton(
            btn_row,
            text=self.i18n.t("btn_stop"),
            command=self._on_stop,
            theme_mgr=self.theme_mgr,
            pady=6,
        )
        self.btn_stop.pack(side=tk.RIGHT, padx=(10, 0))

        self.btn_open = BwButton(
            btn_row,
            text=self.i18n.t("btn_open_out"),
            command=self._on_open_out,
            primary=True,
            theme_mgr=self.theme_mgr,
            pady=6,
        )
        self.btn_open.pack(side=tk.RIGHT)
        self.btn_open.set_enabled(False)

    def reset_view(self):
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")
        self.pbar.set_value(0)
        self.lbl_pct.config(text="0%")
        self.set_state("extract")
        self.output_directory = None
        self.is_running = True
        self.btn_stop.set_enabled(True)
        self.btn_back.set_enabled(False)
        self.btn_open.set_enabled(False)

    def set_progress(self, val: int):
        self.pbar.set_value(val)
        self.lbl_pct.config(text=f"{val}%")

    def set_state(self, state_name: str):
        key = f"state_{state_name}"
        self.current_state_key = key if key in self.i18n.TRANSLATIONS.get("en", {}) else "state_idle"
        state_translated = self.i18n.t(self.current_state_key) if self.current_state_key else state_name
        self.lbl_state.config(text=f"{self.i18n.t('log_state_label')} {state_translated}")

    def append_log(self, text: str):
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, text + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def mark_completed(self, success: bool, out_dir: str = None):
        self.is_running = False
        self.output_directory = out_dir
        self.btn_stop.set_enabled(False)
        self.btn_back.set_enabled(True)
        if success:
            self.set_progress(100)
            self.set_state("done")
            if out_dir and os.path.exists(out_dir):
                self.btn_open.set_enabled(True)
        else:
            self.set_state("failed")

    def mark_cancelled(self):
        self.is_running = False
        self.btn_stop.set_enabled(False)
        self.btn_back.set_enabled(True)
        self.set_state("cancelled")

    def _on_stop(self):
        if self.is_running:
            self.btn_stop.set_enabled(False)
            self.router.cancel_current_build()

    def _on_open_out(self):
        if self.output_directory:
            open_system_folder(self.output_directory)

    def apply_i18n(self):
        self.lbl_title.config(text=self.i18n.t("log_title"))
        state_translated = self.i18n.t(self.current_state_key)
        self.lbl_state.config(text=f"{self.i18n.t('log_state_label')} {state_translated}")
        self.btn_back.set_text(self.i18n.t("btn_back_to_menu"))
        self.btn_stop.set_text(self.i18n.t("btn_stop"))
        self.btn_open.set_text(self.i18n.t("btn_open_out"))

    def apply_theme(self, colors):
        bg = colors["bg"]
        fg = colors["fg"]
        border = colors["border"]
        console_bg = colors["console_bg"]
        console_fg = colors["console_fg"]

        colorize_tree(self, bg)
        self.config(bg=bg)

        self.lbl_title.config(bg=bg, fg=fg)
        self.lbl_pct.config(bg=bg, fg=fg)
        self.lbl_state.config(bg=bg, fg=fg)

        self.txt_log.config(
            bg=console_bg,
            fg=console_fg,
            insertbackground=console_fg,
            selectbackground=colors["select_bg"],
            selectforeground=colors["select_fg"],
            highlightthickness=1,
            highlightbackground=border,
            highlightcolor=colors["border_focus"],
        )
