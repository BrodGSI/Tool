"""Theme Engine for BrodGSI GUI (Black & Neon Green and Monochrome themes)."""

import subprocess
import sys
import tkinter as tk


def detect_system_dark_mode() -> bool:
    """Detects whether host OS is using dark mode."""
    if sys.platform == "win32":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return val == 0
        except Exception:
            return False

    elif sys.platform == "darwin":
        try:
            res = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=1,
            )
            return "Dark" in (res.stdout or "")
        except Exception:
            return False

    else:
        try:
            res = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True,
                text=True,
                timeout=1,
            )
            out = (res.stdout or "").lower()
            if "dark" in out:
                return True
        except Exception:
            pass

    return False


# Primary theme: Black & Neon Green
NEON_PALETTE = {
    "name": "neon",
    "bg": "#0a0d0a",
    "surface": "#101610",
    "card": "#131a13",
    "border": "#00ff66",
    "border_focus": "#39ff14",
    "fg": "#00ff66",
    "fg_bright": "#39ff14",
    "fg_text": "#e2ffe2",
    "fg_dim": "#009933",
    "btn_bg": "#101810",
    "btn_fg": "#00ff66",
    "btn_hover": "#003814",
    "btn_active": "#005520",
    "btn_border": "#00ff66",
    "btn_primary_bg": "#00ff66",
    "btn_primary_fg": "#000000",
    "btn_primary_hover": "#39ff14",
    "btn_primary_active": "#00cc55",
    "entry_bg": "#0c120c",
    "entry_fg": "#00ff66",
    "entry_border": "#00cc55",
    "console_bg": "#060906",
    "console_fg": "#00ff66",
    "select_bg": "#005520",
    "select_fg": "#00ff66",
    "progress_bg": "#141c14",
    "progress_fill": "#00ff66",
}

DARK_PALETTE = {
    "name": "dark",
    "bg": "#111111",
    "surface": "#1a1a1a",
    "card": "#181818",
    "border": "#3a3a3a",
    "border_focus": "#ffffff",
    "fg": "#ffffff",
    "fg_bright": "#ffffff",
    "fg_text": "#ffffff",
    "fg_dim": "#8c8c8c",
    "btn_bg": "#222222",
    "btn_fg": "#ffffff",
    "btn_hover": "#333333",
    "btn_active": "#444444",
    "btn_border": "#555555",
    "btn_primary_bg": "#ffffff",
    "btn_primary_fg": "#000000",
    "btn_primary_hover": "#d8d8d8",
    "btn_primary_active": "#bebebe",
    "entry_bg": "#161616",
    "entry_fg": "#ffffff",
    "entry_border": "#444444",
    "console_bg": "#0a0a0a",
    "console_fg": "#e2e2e2",
    "select_bg": "#383838",
    "select_fg": "#ffffff",
    "progress_bg": "#262626",
    "progress_fill": "#ffffff",
}

LIGHT_PALETTE = {
    "name": "light",
    "bg": "#ffffff",
    "surface": "#f5f5f5",
    "card": "#fbfbfb",
    "border": "#d0d0d0",
    "border_focus": "#000000",
    "fg": "#000000",
    "fg_bright": "#000000",
    "fg_text": "#000000",
    "fg_dim": "#666666",
    "btn_bg": "#eeeeee",
    "btn_fg": "#000000",
    "btn_hover": "#dfdfdf",
    "btn_active": "#cccccc",
    "btn_border": "#000000",
    "btn_primary_bg": "#000000",
    "btn_primary_fg": "#ffffff",
    "btn_primary_hover": "#333333",
    "btn_primary_active": "#555555",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000",
    "entry_border": "#000000",
    "console_bg": "#fafafa",
    "console_fg": "#111111",
    "select_bg": "#cccccc",
    "select_fg": "#000000",
    "progress_bg": "#e6e6e6",
    "progress_fill": "#000000",
}


def colorize_tree(widget, bg, fg=None):
    """Recursively traverses widget tree and sets background on frames/containers."""
    try:
        w_class = widget.winfo_class()
        if w_class in ("Frame", "Labelframe", "Canvas"):
            widget.config(bg=bg)
    except Exception:
        pass
    for child in widget.winfo_children():
        colorize_tree(child, bg, fg)


class ThemeManager:
    """Manages active color theme and widget styling."""

    def __init__(self, initial_pref: str = "neon"):
        self.preference = initial_pref or "neon"
        self.colors = self._resolve_palette(self.preference)
        self.listeners = []

    def _resolve_palette(self, pref: str) -> dict:
        if pref == "neon":
            return NEON_PALETTE
        elif pref == "dark":
            return DARK_PALETTE
        elif pref == "light":
            return LIGHT_PALETTE
        elif pref == "system":
            return NEON_PALETTE if detect_system_dark_mode() else LIGHT_PALETTE
        return NEON_PALETTE

    def set_preference(self, pref: str):
        self.preference = pref
        self.colors = self._resolve_palette(pref)
        self._notify()

    def get_preference(self) -> str:
        return self.preference

    def is_dark(self) -> bool:
        return self.colors["name"] in ("neon", "dark")

    def add_listener(self, cb):
        if cb not in self.listeners:
            self.listeners.append(cb)

    def remove_listener(self, cb):
        if cb in self.listeners:
            self.listeners.remove(cb)

    def _notify(self):
        for cb in list(self.listeners):
            try:
                cb(self.colors)
            except Exception:
                pass


class BwButton(tk.Frame):
    """High contrast neon/monochrome flat button."""

    def __init__(
        self,
        parent,
        text="",
        command=None,
        primary=False,
        theme_mgr=None,
        font=None,
        padx=12,
        pady=6,
        **kwargs
    ):
        self.theme_mgr = theme_mgr
        self.primary = primary
        self.command = command
        self.is_hovered = False
        self.is_pressed = False
        self.state_enabled = True
        self.font = font or (
            "Segoe UI" if sys.platform == "win32" else "TkDefaultFont",
            10,
            "bold" if primary else "normal",
        )

        super().__init__(parent, highlightthickness=1, cursor="hand2", **kwargs)

        self.label = tk.Label(
            self,
            text=text,
            font=self.font,
            padx=padx,
            pady=pady,
            cursor="hand2",
        )
        self.label.pack(fill=tk.BOTH, expand=True)

        for w in (self, self.label):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_press)
            w.bind("<ButtonRelease-1>", self._on_release)

        if self.theme_mgr:
            self.theme_mgr.add_listener(self.apply_theme)
            self.apply_theme(self.theme_mgr.colors)

    def set_text(self, text):
        self.label.config(text=text)

    def set_enabled(self, enabled: bool):
        self.state_enabled = enabled
        cursor = "hand2" if enabled else "arrow"
        self.config(cursor=cursor)
        self.label.config(cursor=cursor)
        if self.theme_mgr:
            self.apply_theme(self.theme_mgr.colors)

    def _on_enter(self, _):
        if not self.state_enabled:
            return
        self.is_hovered = True
        self._update_colors()

    def _on_leave(self, _):
        if not self.state_enabled:
            return
        self.is_hovered = False
        self.is_pressed = False
        self._update_colors()

    def _on_press(self, _):
        if not self.state_enabled:
            return
        self.is_pressed = True
        self._update_colors()

    def _on_release(self, _):
        if not self.state_enabled:
            return
        was_pressed = self.is_pressed
        self.is_pressed = False
        self._update_colors()
        if was_pressed and self.is_hovered and self.command:
            self.command()

    def apply_theme(self, colors):
        self.colors = colors
        self._update_colors()

    def _update_colors(self):
        c = getattr(self, "colors", NEON_PALETTE)
        if not self.state_enabled:
            bg = c["surface"]
            fg = c["fg_dim"]
            border = c["surface"]
        elif self.primary:
            if self.is_pressed:
                bg = c["btn_primary_active"]
            elif self.is_hovered:
                bg = c["btn_primary_hover"]
            else:
                bg = c["btn_primary_bg"]
            fg = c["btn_primary_fg"]
            border = c["border_focus"]
        else:
            if self.is_pressed:
                bg = c["btn_active"]
            elif self.is_hovered:
                bg = c["btn_hover"]
            else:
                bg = c["btn_bg"]
            fg = c["btn_fg"]
            border = c["btn_border"]

        self.config(bg=border, highlightbackground=border, highlightcolor=border)
        self.label.config(bg=bg, fg=fg)


class BwProgressBar(tk.Canvas):
    """Custom canvas progress bar."""

    def __init__(self, parent, height=14, theme_mgr=None, **kwargs):
        self.theme_mgr = theme_mgr
        self.value = 0.0
        self.colors = NEON_PALETTE
        super().__init__(parent, height=height, highlightthickness=1, **kwargs)
        self.bind("<Configure>", lambda e: self._draw())
        if self.theme_mgr:
            self.theme_mgr.add_listener(self.apply_theme)
            self.apply_theme(self.theme_mgr.colors)

    def set_value(self, val: float):
        self.value = max(0.0, min(100.0, float(val)))
        self._draw()

    def apply_theme(self, colors):
        self.colors = colors
        self.config(
            bg=colors["progress_bg"],
            highlightbackground=colors["border"],
            highlightcolor=colors["border"],
        )
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            return
        fill_w = int((self.value / 100.0) * w)
        if fill_w > 0:
            self.create_rectangle(
                0, 0, fill_w, h, fill=self.colors["progress_fill"], width=0
            )
