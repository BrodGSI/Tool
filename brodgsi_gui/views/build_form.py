"""Build configuration view for BrodGSI GUI."""

import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, ttk

import tools

from ..theme import BwButton, colorize_tree

ROM_TYPES = [
    "auto",
    "generic",
    "pixel",
    "hyperos",
    "miui",
    "oneui",
    "oxygenos",
    "coloros",
    "realmeui",
    "flyme",
    "originos",
    "magicos",
    "emui",
    "harmonyos",
    "myos",
    "redmagic",
    "zenui",
    "rog",
    "zui",
    "xperiaui",
    "transsion",
    "custom",
]

EROFS_COMPRESSORS = list(getattr(tools, "EROFS_COMPRESSORS", ("lz4", "lz4hc", "lzma", "deflate")))


class BuildFormView(tk.Frame):
    """Form view for setting up GSI build parameters."""

    def __init__(self, parent, theme_mgr, i18n, router, settings, mode="file"):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.i18n = i18n
        self.router = router
        self.settings = settings
        self.mode = mode  # "file" or "url"

        self.source_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.tag_var = tk.StringVar()
        self.type_var = tk.StringVar(value=self.settings.last_rom_type or "auto")
        self.fs_var = tk.StringVar(value=self.settings.last_fs_format or "ext4")
        self.compressor_var = tk.StringVar(value="lz4")
        self.compress_var = tk.BooleanVar(value=self.settings.last_compress)
        self.no_merge_var = tk.BooleanVar(value=self.settings.last_no_merge)
        self.no_debloat_var = tk.BooleanVar(value=self.settings.last_no_debloat)
        self.avb_key_var = tk.StringVar()

        self._build_ui()
        self.apply_theme(self.theme_mgr.colors)
        self.theme_mgr.add_listener(self.apply_theme)
        self.i18n.add_listener(self.apply_i18n)

    def _build_ui(self):
        # Scrollable container for smaller screens
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, padx=30, pady=20)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=None, yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        f = self.scroll_frame

        # Source input
        src_lbl_key = "field_source_file" if self.mode == "file" else "field_source_url"
        self.lbl_src = tk.Label(
            f,
            text=self.i18n.t(src_lbl_key),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.lbl_src.pack(fill=tk.X, pady=(0, 2))

        src_row = tk.Frame(f)
        src_row.pack(fill=tk.X, pady=(0, 12))

        self.ent_src = tk.Entry(
            src_row,
            textvariable=self.source_var,
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 10),
            relief="solid",
            bd=1,
        )
        self.ent_src.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        if self.mode == "file":
            self.btn_browse = BwButton(
                src_row,
                text=self.i18n.t("field_browse"),
                command=self._on_browse_file,
                theme_mgr=self.theme_mgr,
                padx=8,
                pady=2,
            )
            self.btn_browse.pack(side=tk.RIGHT, padx=(8, 0))

        # Build Name
        self.lbl_name = tk.Label(
            f,
            text=self.i18n.t("field_build_name"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.lbl_name.pack(fill=tk.X, pady=(0, 2))

        self.ent_name = tk.Entry(
            f,
            textvariable=self.name_var,
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 10),
            relief="solid",
            bd=1,
        )
        self.ent_name.pack(fill=tk.X, ipady=4, pady=(0, 2))

        self.hint_name = tk.Label(
            f,
            text=self.i18n.t("field_build_name_hint"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 8),
            anchor="w",
        )
        self.hint_name.pack(fill=tk.X, pady=(0, 12))

        # ROM Type & Tag row
        type_tag_row = tk.Frame(f)
        type_tag_row.pack(fill=tk.X, pady=(0, 12))

        # Left: ROM Type
        left_box = tk.Frame(type_tag_row)
        left_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.lbl_type = tk.Label(
            left_box,
            text=self.i18n.t("field_rom_type"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.lbl_type.pack(fill=tk.X, pady=(0, 2))

        self.cb_type = ttk.Combobox(
            left_box,
            textvariable=self.type_var,
            values=ROM_TYPES,
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 10),
        )
        self.cb_type.pack(fill=tk.X, ipady=3)

        # Right: Tag
        right_box = tk.Frame(type_tag_row)
        right_box.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        self.lbl_tag = tk.Label(
            right_box,
            text=self.i18n.t("field_tag"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.lbl_tag.pack(fill=tk.X, pady=(0, 2))

        self.ent_tag = tk.Entry(
            right_box,
            textvariable=self.tag_var,
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 10),
            relief="solid",
            bd=1,
        )
        self.ent_tag.pack(fill=tk.X, ipady=4)

        # Filesystem Format
        self.lbl_fs = tk.Label(
            f,
            text=self.i18n.t("field_filesystem"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.lbl_fs.pack(fill=tk.X, pady=(5, 2))

        fs_row = tk.Frame(f)
        fs_row.pack(fill=tk.X, pady=(0, 12))

        self.rb_ext4 = tk.Radiobutton(
            fs_row,
            text=self.i18n.t("field_fs_ext4"),
            variable=self.fs_var,
            value="ext4",
            anchor="w",
            cursor="hand2",
            command=self._on_fs_changed,
        )
        self.rb_ext4.pack(anchor="w", pady=1)

        erofs_sub_row = tk.Frame(fs_row)
        erofs_sub_row.pack(fill=tk.X, pady=1)

        self.rb_erofs = tk.Radiobutton(
            erofs_sub_row,
            text=self.i18n.t("field_fs_erofs"),
            variable=self.fs_var,
            value="erofs",
            anchor="w",
            cursor="hand2",
            command=self._on_fs_changed,
        )
        self.rb_erofs.pack(side=tk.LEFT)

        self.lbl_comp = tk.Label(
            erofs_sub_row,
            text=f" {self.i18n.t('field_erofs_compressor')} ",
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 9),
        )
        self.lbl_comp.pack(side=tk.LEFT, padx=(10, 4))

        self.cb_compressor = ttk.Combobox(
            erofs_sub_row,
            textvariable=self.compressor_var,
            values=EROFS_COMPRESSORS,
            state="readonly",
            width=8,
        )
        self.cb_compressor.pack(side=tk.LEFT)

        # AVB Key
        self.lbl_avb = tk.Label(
            f,
            text=self.i18n.t("field_avb_key"),
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
            anchor="w",
        )
        self.lbl_avb.pack(fill=tk.X, pady=(5, 2))

        avb_row = tk.Frame(f)
        avb_row.pack(fill=tk.X, pady=(0, 12))

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

        # Checkbox Options Group
        self.opts_box = tk.LabelFrame(
            f,
            text=f" {self.i18n.t('options_group')} ",
            padx=12,
            pady=8,
            font=("Segoe UI" if sys.platform == "win32" else "TkDefaultFont", 10, "bold"),
        )
        self.opts_box.pack(fill=tk.X, pady=(0, 18))

        self.chk_compress = tk.Checkbutton(
            self.opts_box,
            text=self.i18n.t("opt_compress"),
            variable=self.compress_var,
            anchor="w",
            cursor="hand2",
        )
        self.chk_compress.pack(fill=tk.X, pady=2)

        self.chk_no_merge = tk.Checkbutton(
            self.opts_box,
            text=self.i18n.t("opt_no_merge"),
            variable=self.no_merge_var,
            anchor="w",
            cursor="hand2",
        )
        self.chk_no_merge.pack(fill=tk.X, pady=2)

        self.chk_no_debloat = tk.Checkbutton(
            self.opts_box,
            text=self.i18n.t("opt_no_debloat"),
            variable=self.no_debloat_var,
            anchor="w",
            cursor="hand2",
        )
        self.chk_no_debloat.pack(fill=tk.X, pady=2)

        # Action Buttons
        btn_row = tk.Frame(f)
        btn_row.pack(fill=tk.X, pady=(10, 0))

        self.btn_start = BwButton(
            btn_row,
            text=self.i18n.t("btn_start_build"),
            command=self._on_start,
            primary=True,
            theme_mgr=self.theme_mgr,
            pady=10,
        )
        self.btn_start.pack(side=tk.RIGHT, padx=(10, 0))

        self.btn_back = BwButton(
            btn_row,
            text=self.i18n.t("btn_back"),
            command=lambda: self.router.navigate("build_menu"),
            theme_mgr=self.theme_mgr,
            pady=8,
        )
        self.btn_back.pack(side=tk.LEFT)

    def _on_fs_changed(self):
        state = "readonly" if self.fs_var.get() == "erofs" else "disabled"
        self.cb_compressor.config(state=state)

    def _on_browse_file(self):
        filetypes = [
            (
                "Firmware packages & images",
                "*.zip;*.tar;*.bin;*.img;*.pac;*.kdz;*.ozip;*.sin;*.7z;*.gz",
            ),
            ("All files", "*.*"),
        ]
        chosen = filedialog.askopenfilename(filetypes=filetypes)
        if chosen:
            self.source_var.set(chosen)
            # Auto-suggest name if empty
            if not self.name_var.get().strip():
                base = os.path.splitext(os.path.basename(chosen))[0]
                clean_name = re.sub(r"[^A-Za-z0-9_-]", "_", base).strip("_")[:32]
                self.name_var.set(clean_name or "gsi_build")

    def _on_browse_avb(self):
        filetypes = [("RSA Private Key", "*.pem;*.key"), ("All files", "*.*")]
        chosen = filedialog.askopenfilename(filetypes=filetypes)
        if chosen:
            self.avb_key_var.set(chosen)

    def _on_start(self):
        source = self.source_var.get().strip()
        name = self.name_var.get().strip()

        if not name:
            from tkinter import messagebox

            messagebox.showwarning(self.i18n.t("app_title"), self.i18n.t("error_name_empty"))
            return

        if not source:
            from tkinter import messagebox

            key = "error_file_empty" if self.mode == "file" else "error_url_empty"
            messagebox.showwarning(self.i18n.t("app_title"), self.i18n.t(key))
            return

        if self.mode == "file" and not os.path.exists(source):
            from tkinter import messagebox

            messagebox.showerror(
                self.i18n.t("app_title"),
                self.i18n.t("error_file_not_found", path=source),
            )
            return

        # Save settings for next time
        self.settings.last_rom_type = self.type_var.get()
        self.settings.last_fs_format = self.fs_var.get()
        self.settings.last_compress = self.compress_var.get()
        self.settings.last_no_merge = self.no_merge_var.get()
        self.settings.last_no_debloat = self.no_debloat_var.get()
        self.settings.save()

        fs_format = self.compressor_var.get() if self.fs_var.get() == "erofs" else None

        build_args = {
            "name": name,
            "source": source,
            "type": self.type_var.get() or "auto",
            "add": self.tag_var.get().strip(),
            "compress": self.compress_var.get(),
            "no_merge": self.no_merge_var.get(),
            "no_debloat": self.no_debloat_var.get(),
            "format": fs_format,
            "avb_key": self.avb_key_var.get().strip() or None,
        }

        self.router.start_build(build_args)

    def apply_i18n(self):
        src_lbl_key = "field_source_file" if self.mode == "file" else "field_source_url"
        self.lbl_src.config(text=self.i18n.t(src_lbl_key))
        if hasattr(self, "btn_browse"):
            self.btn_browse.set_text(self.i18n.t("field_browse"))
        self.lbl_name.config(text=self.i18n.t("field_build_name"))
        self.hint_name.config(text=self.i18n.t("field_build_name_hint"))
        self.lbl_type.config(text=self.i18n.t("field_rom_type"))
        self.lbl_tag.config(text=self.i18n.t("field_tag"))
        self.lbl_fs.config(text=self.i18n.t("field_filesystem"))
        self.rb_ext4.config(text=self.i18n.t("field_fs_ext4"))
        self.rb_erofs.config(text=self.i18n.t("field_fs_erofs"))
        self.lbl_comp.config(text=f" {self.i18n.t('field_erofs_compressor')} ")
        self.lbl_avb.config(text=self.i18n.t("field_avb_key"))
        self.btn_avb_browse.set_text(self.i18n.t("field_browse"))
        self.opts_box.config(text=f" {self.i18n.t('options_group')} ")
        self.chk_compress.config(text=self.i18n.t("opt_compress"))
        self.chk_no_merge.config(text=self.i18n.t("opt_no_merge"))
        self.chk_no_debloat.config(text=self.i18n.t("opt_no_debloat"))
        self.btn_start.set_text(self.i18n.t("btn_start_build"))
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
        self.canvas.config(bg=bg, highlightbackground=bg)
        self.scroll_frame.config(bg=bg)
        self.lbl_src.config(bg=bg, fg=fg)
        self.lbl_name.config(bg=bg, fg=fg)
        self.hint_name.config(bg=bg, fg=fg_dim)
        self.lbl_type.config(bg=bg, fg=fg)
        self.lbl_tag.config(bg=bg, fg=fg)
        self.lbl_fs.config(bg=bg, fg=fg)
        self.lbl_comp.config(bg=bg, fg=fg)
        self.lbl_avb.config(bg=bg, fg=fg)

        for ent in (self.ent_src, self.ent_name, self.ent_tag, self.ent_avb):
            ent.config(
                bg=entry_bg,
                fg=entry_fg,
                insertbackground=entry_fg,
                highlightthickness=1,
                highlightbackground=border,
                highlightcolor=colors["border_focus"],
            )

        for rb in (self.rb_ext4, self.rb_erofs):
            rb.config(
                bg=bg,
                fg=fg,
                activebackground=bg,
                activeforeground=fg,
                selectcolor=surf,
                highlightbackground=bg,
            )

        self.opts_box.config(
            bg=surf,
            fg=fg,
            highlightbackground=border,
            highlightthickness=1,
            bd=0,
        )
        for chk in (self.chk_compress, self.chk_no_merge, self.chk_no_debloat):
            chk.config(
                bg=surf,
                fg=fg,
                activebackground=surf,
                activeforeground=fg,
                selectcolor=bg,
                highlightbackground=surf,
            )
