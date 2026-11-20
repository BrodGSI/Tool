"""Main application window and screen router for BrodGSI GUI."""

import os
import sys
import tkinter as tk

from .i18n import I18N
from .runner import BuildRunner
from .settings import AppSettings
from .settings_dialog import SettingsDialog
from .theme import ThemeManager
from .views.build_form import BuildFormView
from .views.clean_view import CleanView
from .views.header import HeaderBar
from .views.list_view import ListView
from .views.log_view import LogView
from .views.menu import BuildSubmenuView, MainMenuView
from .views.rebuild_view import RebuildView


def _find_icon_path() -> str | None:
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    p1 = os.path.join(exe_dir, "icon.png")
    if os.path.isfile(p1):
        return p1
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p2 = os.path.join(meipass, "icon.png")
        if os.path.isfile(p2):
            return p2
    p3 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icon.png"))
    if os.path.isfile(p3):
        return p3
    if os.path.isfile("icon.png"):
        return os.path.abspath("icon.png")
    return None


class BrodGsiApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = AppSettings()

        # Set application icon
        self.icon_image = None
        icon_path = _find_icon_path()
        if icon_path:
            try:
                self.icon_image = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, self.icon_image)
            except Exception:
                pass
            if sys.platform == "win32":
                ico_path = icon_path.replace(".png", ".ico")
                if os.path.isfile(ico_path):
                    try:
                        self.root.iconbitmap(ico_path)
                    except Exception:
                        pass

        # Initialize managers
        self.theme_mgr = ThemeManager(self.settings.theme)
        self.i18n = I18N(self.settings.language)

        self.root.title(self.i18n.t("app_title"))
        self.root.geometry("740x600")
        self.root.minsize(640, 520)

        # Runner
        self.runner = BuildRunner(
            on_progress=self._on_runner_progress,
            on_state=self._on_runner_state,
            on_log=self._on_runner_log,
            on_finish=self._on_runner_finish,
        )

        self.views = {}
        self.current_view_name = "menu"

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

        # Start periodic polling for runner messages
        self._poll_runner()

    def _build_ui(self):
        # Header bar
        self.header = HeaderBar(
            self.root,
            theme_mgr=self.theme_mgr,
            i18n=self.i18n,
            on_settings_click=self.open_settings,
            on_navigate_root=lambda: self.navigate("menu"),
        )
        self.header.pack(side=tk.TOP, fill=tk.X)

        # Main content viewport
        self.viewport = tk.Frame(self.root)
        self.viewport.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Instantiate views
        self.views["menu"] = MainMenuView(
            self.viewport, self.theme_mgr, self.i18n, self
        )
        self.views["build_menu"] = BuildSubmenuView(
            self.viewport, self.theme_mgr, self.i18n, self
        )
        self.views["build_file"] = BuildFormView(
            self.viewport, self.theme_mgr, self.i18n, self, self.settings, mode="file"
        )
        self.views["build_url"] = BuildFormView(
            self.viewport, self.theme_mgr, self.i18n, self, self.settings, mode="url"
        )
        self.views["rebuild"] = RebuildView(
            self.viewport, self.theme_mgr, self.i18n, self, self.settings
        )
        self.views["list"] = ListView(
            self.viewport, self.theme_mgr, self.i18n, self
        )
        self.views["clean"] = CleanView(
            self.viewport, self.theme_mgr, self.i18n, self
        )
        self.views["log"] = LogView(
            self.viewport, self.theme_mgr, self.i18n, self
        )

        self.navigate("menu")

    def navigate(self, view_name: str, **kwargs):
        if view_name not in self.views:
            return

        for name, v in self.views.items():
            v.pack_forget()

        self.current_view_name = view_name
        active_v = self.views[view_name]

        # Extra hooks
        if view_name == "list":
            active_v.load_entries()
        elif view_name == "rebuild":
            active_v.refresh_names()
            if "initial_name" in kwargs and kwargs["initial_name"]:
                active_v.name_var.set(kwargs["initial_name"])
        elif view_name == "clean":
            active_v.scan_disk()

        active_v.pack(fill=tk.BOTH, expand=True)
        self._update_breadcrumbs()

    def _update_breadcrumbs(self):
        crumbs = {
            "menu": self.i18n.t("crumb_root"),
            "build_menu": f"{self.i18n.t('crumb_root')} > {self.i18n.t('crumb_build_menu')}",
            "build_file": f"{self.i18n.t('crumb_root')} > {self.i18n.t('crumb_build_menu')} > {self.i18n.t('crumb_build_file')}",
            "build_url": f"{self.i18n.t('crumb_root')} > {self.i18n.t('crumb_build_menu')} > {self.i18n.t('crumb_build_url')}",
            "rebuild": f"{self.i18n.t('crumb_root')} > {self.i18n.t('crumb_rebuild')}",
            "list": f"{self.i18n.t('crumb_root')} > {self.i18n.t('crumb_list')}",
            "clean": f"{self.i18n.t('crumb_root')} > {self.i18n.t('crumb_clean')}",
            "log": f"{self.i18n.t('crumb_root')} > {self.i18n.t('crumb_log')}",
        }
        self.header.set_breadcrumb(crumbs.get(self.current_view_name, ""))

    def open_settings(self):
        SettingsDialog(self.root, self.theme_mgr, self.i18n, self.settings)

    def start_build(self, build_args: dict):
        log_v: LogView = self.views["log"]
        log_v.reset_view()
        self.navigate("log")
        self.runner.start_build(build_args)

    def start_rebuild(self, rebuild_args: dict):
        log_v: LogView = self.views["log"]
        log_v.reset_view()
        self.navigate("log")
        self.runner.start_rebuild(rebuild_args)

    def cancel_current_build(self):
        self.runner.cancel()

    def _on_runner_progress(self, val: int):
        log_v: LogView = self.views["log"]
        log_v.set_progress(val)

    def _on_runner_state(self, state: str):
        log_v: LogView = self.views["log"]
        log_v.set_state(state)

    def _on_runner_log(self, text: str):
        log_v: LogView = self.views["log"]
        log_v.append_log(text)

    def _on_runner_finish(self, success: bool, out_dir: str, cancelled: bool):
        log_v: LogView = self.views["log"]
        if cancelled:
            log_v.mark_cancelled()
        else:
            log_v.mark_completed(success, out_dir)

    def _poll_runner(self):
        self.runner.poll_messages()
        self.root.after(100, self._poll_runner)

    def apply_i18n(self):
        self.root.title(self.i18n.t("app_title"))
        self._update_breadcrumbs()

    def apply_theme(self, colors):
        bg = colors["bg"]
        self.root.config(bg=bg)
        self.viewport.config(bg=bg)


def main():
    root = tk.Tk()
    _ = BrodGsiApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
