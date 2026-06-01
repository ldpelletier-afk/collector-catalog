#!/usr/bin/env bash
# Build the desktop bundle.  After this finishes you'll have:
#   macOS:  dist/Collector Catalog.app
#   Other:  dist/CollectorCatalog/CollectorCatalog
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

echo "→ Cleaning previous build artifacts"
rm -rf build dist

echo "→ Installing build dependencies"
python3 -m pip install --quiet --upgrade pyinstaller Pillow

echo "→ Building bundle with PyInstaller"
python3 -m PyInstaller CollectorCatalog.spec --noconfirm --log-level WARN

if [[ "$(uname -s)" == "Darwin" ]]; then
    APP="dist/Collector Catalog.app"
    if [[ -d "$APP" ]]; then
        echo
        echo "✓ Built:  $APP"
        echo "  Double-click it in Finder, or:  open \"$APP\""
        echo
        echo "  First launch on macOS:  right-click → Open  (Gatekeeper)"
    else
        echo "✗ Build finished but no .app found in dist/"
        exit 1
    fi
else
    echo "✓ Built:  dist/CollectorCatalog/"
fi
