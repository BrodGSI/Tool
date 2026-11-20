#!/usr/bin/env python3
"""Cross-platform packaging script for BrodGSI releases."""

import argparse
import os
import shutil
import sys
import tarfile
import zipfile


def create_zip(archive_path: str, source_dir: str):
    print(f"[*] Creating ZIP archive: {archive_path}...")
    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
        allowZip64=True,
    ) as zf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source_dir)
                zf.write(full_path, arcname=rel_path)


def create_tar_gz(archive_path: str, source_dir: str):
    print(f"[*] Creating tar.gz archive: {archive_path}...")
    with tarfile.open(archive_path, "w:gz", compresslevel=6) as tar:
        for item in sorted(os.listdir(source_dir)):
            item_path = os.path.join(source_dir, item)
            tar.add(item_path, arcname=item)


def main():
    parser = argparse.ArgumentParser(description="Package BrodGSI for release.")
    parser.add_argument("--name", required=True, help="Base name of release archive")
    parser.add_argument("--format", choices=["zip", "tar.gz"], required=True, help="Archive format")
    parser.add_argument("--dist-dir", default="dist", help="Directory with built binaries")
    parser.add_argument("--include-patches", action="store_true", help="Include patches folder")
    args = parser.parse_args()

    pkg_dir = "build_package"
    if os.path.exists(pkg_dir):
        shutil.rmtree(pkg_dir, ignore_errors=True)
    os.makedirs(pkg_dir, exist_ok=True)

    # 1. Copy binaries
    bin_files = os.listdir(args.dist_dir) if os.path.exists(args.dist_dir) else []
    found_binaries = 0
    for bf in bin_files:
        src = os.path.join(args.dist_dir, bf)
        if os.path.isfile(src) and ("brodgsi" in bf.lower()):
            dst = os.path.join(pkg_dir, bf)
            shutil.copy2(src, dst)
            if not bf.endswith(".exe"):
                try:
                    os.chmod(dst, 0o755)
                except Exception:
                    pass
            found_binaries += 1
            print(f"[*] Added binary: {bf}")

    if found_binaries == 0:
        print(f"[!] Warning: No brodgsi binaries found in {args.dist_dir}")

    # 2. Copy tools directory
    if os.path.isdir("tools"):
        shutil.copytree("tools", os.path.join(pkg_dir, "tools"))
        print("[*] Added tools/ directory")

    # 3. Copy docs, license & icons
    for doc in ("README.md", "LICENSE", "AUTHORS", "NOTICE", "icon.png", "icon.ico", "icon.icns"):
        if os.path.isfile(doc):
            shutil.copy2(doc, os.path.join(pkg_dir, doc))

    # 4. Optional: include patches
    if args.include_patches and os.path.isdir("patches"):
        print("[*] Adding patches/ directory (this may take a few moments)...")
        shutil.copytree("patches", os.path.join(pkg_dir, "patches"))

    # 5. Build archive
    out_archive = f"{args.name}.{args.format}"
    if args.format == "zip":
        create_zip(out_archive, pkg_dir)
    else:
        create_tar_gz(out_archive, pkg_dir)

    size_mb = os.path.getsize(out_archive) / (1024 * 1024)
    print(f"[OK] Package created: {out_archive} ({size_mb:.2f} MB)")

    # GitHub Release limit check (2 GiB)
    if size_mb > 2000:
        print(f"[ERROR] Archive exceeds GitHub Release 2GB limit! ({size_mb:.2f} MB)")
        sys.exit(1)

    # Clean up staging folder
    shutil.rmtree(pkg_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
