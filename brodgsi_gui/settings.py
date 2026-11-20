"""Settings storage for BrodGSI GUI."""

import json
import os

CONFIG_FILENAME = ".brodgsi_gui_settings.json"


def get_config_path() -> str:
    """Finds writable location for user settings."""
    home = os.path.expanduser("~")
    if os.path.isdir(home) and os.access(home, os.W_OK):
        return os.path.join(home, CONFIG_FILENAME)
    return CONFIG_FILENAME


class AppSettings:
    def __init__(self):
        self.path = get_config_path()
        self.theme = "neon"
        self.language = "system"
        self.last_rom_type = "auto"
        self.last_fs_format = "ext4"
        self.last_compress = False
        self.last_no_merge = False
        self.last_no_debloat = False
        self.load()

    def load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.theme = data.get("theme", "system")
                    self.language = data.get("language", "system")
                    self.last_rom_type = data.get("last_rom_type", "auto")
                    self.last_fs_format = data.get("last_fs_format", "ext4")
                    self.last_compress = bool(data.get("last_compress", False))
                    self.last_no_merge = bool(data.get("last_no_merge", False))
                    self.last_no_debloat = bool(data.get("last_no_debloat", False))
        except Exception:
            pass

    def save(self):
        try:
            data = {
                "theme": self.theme,
                "language": self.language,
                "last_rom_type": self.last_rom_type,
                "last_fs_format": self.last_fs_format,
                "last_compress": self.last_compress,
                "last_no_merge": self.last_no_merge,
                "last_no_debloat": self.last_no_debloat,
            }
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
