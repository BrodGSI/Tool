"""Internationalization (i18n) module for BrodGSI GUI."""

import locale
import os
import sys

TRANSLATIONS = {
    "en": {
        "app_title": "BrodGSI Tool",
        "header_settings_btn": "[ ⚙ Settings ]",
        "crumb_root": "Menu",
        "crumb_build_menu": "Build GSI",
        "crumb_build_file": "Build from File",
        "crumb_build_url": "Build from URL",
        "crumb_rebuild": "Rebuild GSI",
        "crumb_list": "Build List",
        "crumb_clean": "Disk Cleanup",
        "crumb_log": "Build Progress",
        # Main menu
        "menu_title": "BrodGSI Control Center",
        "menu_desc": "Monochrome Android GSI builder & patcher",
        "btn_build_menu": "1. Build GSI",
        "btn_rebuild_menu": "2. Rebuild GSI",
        "btn_list_menu": "3. Build History & Images",
        "btn_clean_menu": "4. Clean Temporary Files",
        "btn_exit": "Exit",
        # Build submenu
        "build_sub_title": "Select Build Source",
        "build_sub_desc": "Choose how you want to provide stock Android firmware",
        "btn_build_from_file": "Build from Local File",
        "btn_build_from_file_desc": "Use an existing archive or image on your drive (.zip, .tar, .bin, .img, .pac, .kdz, .ozip, .sin)",
        "btn_build_from_url": "Build from Firmware URL",
        "btn_build_from_url_desc": "Download firmware directly using fast multi-threaded downloader",
        "btn_back_to_menu": "< Back to Main Menu",
        "btn_back": "< Back",
        # Build forms
        "field_source_file": "Firmware File:",
        "field_source_url": "Firmware Download URL:",
        "field_browse": "Browse...",
        "field_build_name": "Build Name:",
        "field_build_name_hint": "Unique identifier for output directory (e.g. raven, miui14, oneui6)",
        "field_rom_type": "ROM Type:",
        "field_rom_type_hint": "auto or specific vendor (e.g. pixel, oneui, hyperos, miui, oxygenos)",
        "field_tag": "Additional Tag (--add):",
        "field_tag_hint": "Optional tag appended to build name (e.g. test, v1.0, debloated)",
        "field_filesystem": "Filesystem Format:",
        "field_fs_ext4": "ext4 (Default, maximum device compatibility)",
        "field_fs_erofs": "EROFS (Compressed, smaller size, needs kernel support)",
        "field_erofs_compressor": "EROFS Compressor:",
        "field_avb_key": "AVB Signing Key (.pem):",
        "field_avb_key_default": "AOSP Test Key (bundled)",
        "field_avb_key_custom": "Custom Private RSA Key...",
        "options_group": "Build Options:",
        "opt_compress": "Create .zip archive with images (--compress)",
        "opt_no_merge": "Separate partition images instead of merging into system (--no-merge)",
        "opt_no_debloat": "Disable debloat (keep vendor stock apps) (--no-debloat)",
        "btn_start_build": "START BUILD",
        "btn_start_rebuild": "START REBUILD",
        # Rebuild view
        "rebuild_title": "Rebuild Existing GSI",
        "rebuild_desc": "Recreate GSI images using modified filesystem tree in tmp/<name>/images",
        "rebuild_select": "Select Existing Build:",
        "rebuild_no_builds": "No prior builds found in tmp/gsilist.json",
        # List view
        "list_title": "Build History & Generated Images",
        "list_desc": "Previously generated GSI builds from tmp/gsilist.json",
        "list_empty": "No builds recorded yet.",
        "list_col_id": "#",
        "list_col_name": "Build Name",
        "list_col_status": "Status",
        "list_col_images": "Output Images",
        "list_status_exists": "[EXISTS]",
        "list_status_missing": "[MISSING]",
        "btn_refresh": "Refresh",
        "btn_open_folder": "Open Output Folder",
        "btn_rebuild_this": "Rebuild Selected",
        # Clean view
        "clean_title": "Clean Temporary Files & Outputs",
        "clean_desc": "Free disk space by deleting build workspace files",
        "clean_scan": "Analyzing directories...",
        "clean_found": "Found {count} items taking {size} on disk.",
        "clean_opt_tmp": "Clean workspace directory (tmp/)",
        "clean_opt_out": "Clean build outputs directory (out/)",
        "btn_clean_now": "DELETE SELECTED FILES",
        "clean_confirm_title": "Confirm Deletion",
        "clean_confirm_msg": "Are you sure you want to permanently delete the selected files? Total size: {size}",
        "clean_done": "Cleanup completed. Freed {size}.",
        # Log view
        "log_title": "Build Execution",
        "log_state_label": "State:",
        "log_progress_label": "Progress:",
        "btn_stop": "ABORT / STOP",
        "btn_open_out": "Open Output Directory",
        "state_idle": "Idle",
        "state_extract": "Extracting firmware",
        "state_unpack": "Unpacking images",
        "state_patch": "Applying patches",
        "state_prepare": "Preparing filesystem",
        "state_mke2fs": "Generating partition image",
        "state_sign": "Signing image with AVB",
        "state_compress": "Compressing output",
        "state_done": "Completed successfully",
        "state_failed": "Build failed with errors",
        "state_cancelled": "Cancelled by user",
        # Settings
        "settings_title": "Settings",
        "settings_lang_label": "Interface Language:",
        "settings_lang_system": "System Default ({lang})",
        "settings_lang_en": "English",
        "settings_lang_ru": "Русский (Russian)",
        "settings_theme_label": "Color Theme (Black & White):",
        "settings_theme_system": "System Default ({theme})",
        "settings_theme_dark": "Dark Theme (Monochrome)",
        "settings_theme_light": "Light Theme (Monochrome)",
        "settings_tools_status": "Native Tools Status:",
        "settings_status_ok": "[OK]",
        "settings_status_missing": "[NOT FOUND]",
        "btn_save_close": "Save & Close",
        # Errors & notices
        "error_name_empty": "Please specify a build name.",
        "error_file_empty": "Please select a firmware file.",
        "error_file_not_found": "Selected file does not exist: {path}",
        "error_url_empty": "Please enter a valid firmware URL.",
        "error_build_in_progress": "A build is currently running. Please wait or abort it.",
        "error_lock_busy": "Another build process holds the build lock.",
        "notice_success": "Build completed successfully!",
        "notice_failed": "Build failed. See log output above.",
        "notice_cancelled": "Build process was cancelled.",
    },
    "ru": {
        "app_title": "BrodGSI Tool",
        "header_settings_btn": "[ ⚙ Настройки ]",
        "crumb_root": "Меню",
        "crumb_build_menu": "Сборка GSI",
        "crumb_build_file": "Сборка из файла",
        "crumb_build_url": "Сборка по ссылке",
        "crumb_rebuild": "Пересборка GSI",
        "crumb_list": "Список сборок",
        "crumb_clean": "Очистка диска",
        "crumb_log": "Ход сборки",
        # Главное меню
        "menu_title": "Центр управления BrodGSI",
        "menu_desc": "Черно-белая утилита портирования и сборки Generic System Image",
        "btn_build_menu": "1. Собрать GSI",
        "btn_rebuild_menu": "2. Пересобрать GSI",
        "btn_list_menu": "3. Список сборок и образов",
        "btn_clean_menu": "4. Очистка временных файлов",
        "btn_exit": "Выход",
        # Подменю сборки
        "build_sub_title": "Выберите источник прошивки",
        "build_sub_desc": "Укажите, откуда загружать исходную прошивку Android",
        "btn_build_from_file": "Собрать GSI из файла",
        "btn_build_from_file_desc": "Использовать локальный файл прошивки (.zip, .tar, .bin, .img, .pac, .kdz, .ozip, .sin)",
        "btn_build_from_url": "Собрать GSI по ссылке",
        "btn_build_from_url_desc": "Скачать прошивку напрямую по прямой ссылке с помощью быстрого загрузчика",
        "btn_back_to_menu": "< Назад в главное меню",
        "btn_back": "< Назад",
        # Формы сборки
        "field_source_file": "Файл прошивки:",
        "field_source_url": "Ссылка на прошивку (URL):",
        "field_browse": "Обзор...",
        "field_build_name": "Имя сборки:",
        "field_build_name_hint": "Идентификатор сборки и папки out/<имя> (например raven, miui14, oneui6)",
        "field_rom_type": "Тип ROM:",
        "field_rom_type_hint": "auto или тип прошивки (например pixel, oneui, hyperos, miui, oxygenos)",
        "field_tag": "Дополнительный тег (--add):",
        "field_tag_hint": "Опциональный тег в названии (например test, v1.0, debloated)",
        "field_filesystem": "Файловая система:",
        "field_fs_ext4": "ext4 (По умолчанию, максимальная совместимость)",
        "field_fs_erofs": "EROFS (Сжатая, меньший размер, требует поддержки ядром)",
        "field_erofs_compressor": "Компрессор EROFS:",
        "field_avb_key": "Ключ подписи AVB (.pem):",
        "field_avb_key_default": "Стандартный тестовый ключ AOSP",
        "field_avb_key_custom": "Свой закрытый RSA ключ...",
        "options_group": "Параметры сборки:",
        "opt_compress": "Сжать итоговые образы в .zip архив (--compress)",
        "opt_no_merge": "Раздельные образы разделов вместо объединения в system (--no-merge)",
        "opt_no_debloat": "Отключить debloat (оставить встроенные приложения вендора) (--no-debloat)",
        "btn_start_build": "ЗАПУСТИТЬ СБОРКУ",
        "btn_start_rebuild": "ЗАПУСТИТЬ ПЕРЕСБОРКУ",
        # Экран пересборки
        "rebuild_title": "Пересборка существующего GSI",
        "rebuild_desc": "Создание образов заново из отредактированных папок в tmp/<name>/images",
        "rebuild_select": "Выберите ранее собранный ROM:",
        "rebuild_no_builds": "Ранее собранные образы не найдены в tmp/gsilist.json",
        # Экран списка
        "list_title": "История сборок и образы",
        "list_desc": "Ранее созданные сборки из tmp/gsilist.json",
        "list_empty": "Записи о сборках отсутствуют.",
        "list_col_id": "№",
        "list_col_name": "Название сборки",
        "list_col_status": "Статус",
        "list_col_images": "Файлы образов",
        "list_status_exists": "[НА ДИСКЕ]",
        "list_status_missing": "[ОТСУТСТВУЕТ]",
        "btn_refresh": "Обновить",
        "btn_open_folder": "Открыть папку",
        "btn_rebuild_this": "Пересобрать выбранное",
        # Экран очистки
        "clean_title": "Очистка временных файлов и диска",
        "clean_desc": "Освобождение дискового пространства удалением рабочих файлов сборки",
        "clean_scan": "Сканирование папок...",
        "clean_found": "Найдено {count} объектов общим объемом {size} на диске.",
        "clean_opt_tmp": "Очистить рабочую папку (tmp/)",
        "clean_opt_out": "Очистить папку готовых образов (out/)",
        "btn_clean_now": "УДАЛИТЬ ВЫБРАННЫЕ ФАЙЛЫ",
        "clean_confirm_title": "Подтверждение удаления",
        "clean_confirm_msg": "Вы уверены, что хотите удалить выбранные файлы? Общий объем: {size}",
        "clean_done": "Очистка завершена. Освобождено {size}.",
        # Экран лога
        "log_title": "Процесс выполнения",
        "log_state_label": "Состояние:",
        "log_progress_label": "Прогресс:",
        "btn_stop": "ПРЕРВАТЬ СБОРКУ",
        "btn_open_out": "Открыть папку с результатом",
        "state_idle": "Ожидание",
        "state_extract": "Распаковка прошивки",
        "state_unpack": "Распаковка образов",
        "state_patch": "Применение патчей",
        "state_prepare": "Подготовка файловой системы",
        "state_mke2fs": "Создание образа раздела",
        "state_sign": "Подпись образа через AVB",
        "state_compress": "Сжатие архива",
        "state_done": "Сборка успешно завершена",
        "state_failed": "Ошибка сборки",
        "state_cancelled": "Прервано пользователем",
        # Настройки
        "settings_title": "Настройки",
        "settings_lang_label": "Язык интерфейса:",
        "settings_lang_system": "Системный по умолчанию ({lang})",
        "settings_lang_en": "English",
        "settings_lang_ru": "Русский",
        "settings_theme_label": "Цветовая тема (Черно-белая):",
        "settings_theme_system": "Системная по умолчанию ({theme})",
        "settings_theme_dark": "Темная тема (Монохромная)",
        "settings_theme_light": "Светлая тема (Монохромная)",
        "settings_tools_status": "Статус встроенных утилит:",
        "settings_status_ok": "[ДОСТУПНО]",
        "settings_status_missing": "[НЕ НАЙДЕНО]",
        "btn_save_close": "Сохранить и закрыть",
        # Ошибки и уведомления
        "error_name_empty": "Пожалуйста, введите имя сборки.",
        "error_file_empty": "Пожалуйста, выберите файл прошивки.",
        "error_file_not_found": "Выбранный файл не существует: {path}",
        "error_url_empty": "Пожалуйста, введите корректный URL прошивки.",
        "error_build_in_progress": "В данный момент уже выполняется сборка.",
        "error_lock_busy": "Другой процесс BrodGSI удерживает блокировку сборки.",
        "notice_success": "Сборка успешно завершена!",
        "notice_failed": "Сборка завершилась с ошибкой. См. вывод выше.",
        "notice_cancelled": "Сборка была прервана пользователем.",
    },
}


def detect_system_lang() -> str:
    """Detects system language code ('ru' or 'en')."""
    try:
        # Check standard locale
        loc = locale.getdefaultlocale()[0] or locale.getlocale()[0]
        if loc and str(loc).lower().startswith("ru"):
            return "ru"
    except Exception:
        pass

    if sys.platform == "win32":
        try:
            import ctypes
            # GetUserDefaultUILanguage returns LANGID. 0x0419 is Russian
            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF
            if lang_id == 0x19:
                return "ru"
        except Exception:
            pass

    for var in ("LANG", "LANGUAGE", "LC_ALL", "LC_MESSAGES"):
        val = os.environ.get(var, "").lower()
        if val.startswith("ru"):
            return "ru"

    return "en"


class I18N:
    """Manages active language and string resolution."""

    def __init__(self, initial_lang: str = "system"):
        self.configured_lang = initial_lang
        self.active_lang = self._resolve_lang(initial_lang)
        self.listeners = []

    def _resolve_lang(self, pref: str) -> str:
        if pref in ("ru", "en"):
            return pref
        return detect_system_lang()

    def set_lang(self, lang_code: str):
        self.configured_lang = lang_code
        new_active = self._resolve_lang(lang_code)
        if new_active != self.active_lang:
            self.active_lang = new_active
            self._notify()

    def get_configured_lang(self) -> str:
        return self.configured_lang

    def get_active_lang(self) -> str:
        return self.active_lang

    def add_listener(self, callback):
        if callback not in self.listeners:
            self.listeners.append(callback)

    def remove_listener(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    def _notify(self):
        for cb in list(self.listeners):
            try:
                cb()
            except Exception:
                pass

    def t(self, key: str, **kwargs) -> str:
        lang_dict = TRANSLATIONS.get(self.active_lang, TRANSLATIONS["en"])
        template = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
        if kwargs:
            try:
                return template.format(**kwargs)
            except Exception:
                return template
        return template
