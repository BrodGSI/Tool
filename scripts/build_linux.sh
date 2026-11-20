#!/usr/bin/env bash
set -euo pipefail

ARCH="${1:-x64}"
echo "[*] Building BrodGSI for Linux ($ARCH)..."

pip install --upgrade pip
pip install -r requirements.txt pyinstaller

python build_binaries.py

mkdir -p package
chmod +x dist/brodgsi-gui dist/brodgsi-cli
cp dist/brodgsi-gui dist/brodgsi-cli README.md LICENSE package/
tar -czvf "brodgsi-linux-${ARCH}.tar.gz" -C package .

echo "[OK] Built brodgsi-linux-${ARCH}.tar.gz"
