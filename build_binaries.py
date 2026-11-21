#!/usr/bin/env python3
"""Build standalone BrodGSI CLI and GUI executables using PyInstaller."""

import argparse
import os
import subprocess
import sys

SEP = ";" if os.name == "nt" else ":"

DATA_ENTRIES = [
    f"tools/apktool{SEP}tools/apktool",
    f"tools/avb{SEP}tools/avb",
    f"tools/image/mke2fs.conf{SEP}tools/image",
]
if os.path.isfile("icon.png"):
    DATA_ENTRIES.append(f"icon.png{SEP}icon.png")

HIDDEN_IMPORTS = [
    "requests",
    "google.protobuf",
    "Crypto",
    "Crypto.PublicKey.RSA",
    "lz4",
    "lz4.frame",
    "brotli",
    "zstandard",
    "py7zr",
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
]


def run_pyinstaller(
    name: str,
    entrypoint: str,
    is_gui: bool = False,
    onefile: bool = True,
    target_arch: str = None,
):
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        name,
        "--clean",
        "-y",
    ]

    if onefile:
        cmd.append("--onefile")

    if is_gui:
        # On Windows and macOS, windowed/noconsole prevents black console window
        cmd.append("--noconsole")
    else:
        cmd.append("--console")

    if target_arch and sys.platform == "darwin":
        cmd.extend(["--target-arch", target_arch])

    if sys.platform == "win32" and os.path.isfile("icon.ico"):
        cmd.extend(["--icon", "icon.ico"])
    elif sys.platform == "darwin" and os.path.isfile("icon.icns"):
        cmd.extend(["--icon", "icon.icns"])
    elif sys.platform not in ("win32", "darwin") and os.path.isfile("icon.png"):
        cmd.extend(["--icon", "icon.png"])

    for data in DATA_ENTRIES:
        cmd.extend(["--add-data", data])

    for hi in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", hi])

    cmd.append(entrypoint)

    print(f"[*] Building {name} from {entrypoint} (gui={is_gui})...")
    print(" ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError(f"PyInstaller build failed for {name} with code {res.returncode}")
    print(f"[OK] Successfully built {name}")


def main():
    parser = argparse.ArgumentParser(description="Build BrodGSI binaries.")
    parser.add_argument("--cli-only", action="store_true", help="Build only CLI binary")
    parser.add_argument("--gui-only", action="store_true", help="Build only GUI binary")
    parser.add_argument("--onedir", action="store_true", help="Build onedir instead of onefile")
    parser.add_argument("--target-arch", help="Target architecture (macOS universal2/x86_64/arm64)")
    args = parser.parse_args()

    onefile = not args.onedir

    # Ensure dependencies
    import importlib.util

    needed = []
    if importlib.util.find_spec("PyInstaller") is None:
        needed.append("pyinstaller")
    if importlib.util.find_spec("PIL") is None:
        needed.append("pillow")

    if needed:
        print(f"[*] Installing build tools: {needed}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *needed])

    build_cli = not args.gui_only
    build_gui = not args.cli_only

    if build_cli:
        run_pyinstaller(
            "brodgsi-cli",
            "cli.py",
            is_gui=False,
            onefile=onefile,
            target_arch=args.target_arch,
        )

    if build_gui:
        run_pyinstaller(
            "brodgsi-gui",
            "gui.py",
            is_gui=True,
            onefile=onefile,
            target_arch=args.target_arch,
        )

    print("[*] Build completed! Executables are located in dist/")


if __name__ == "__main__":
    main()
