#!/usr/bin/env bash
# Build the desktop bundle.  After this finishes you'll have:
#   macOS:  dist/Collector Catalog.app
#   Other:  dist/CollectorCatalog/CollectorCatalog
#
# Pass --install to also replace the copy you actually launch:
#   macOS:  swaps ~/Desktop/Collector Catalog.app and/or the one in
#           /Applications for the freshly built bundle
#   Linux:  refreshes the ~/.local/share/applications launcher (and the
#           Desktop copy of it, if you have one)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

APP_NAME="Collector Catalog"
INSTALL=0
for arg in "$@"; do
    case "$arg" in
        --install) INSTALL=1 ;;
        -h|--help)
            echo "Usage: $0 [--install]"
            echo "  --install   replace the installed copy with the new build"
            exit 0 ;;
        *) echo "Unknown option: $arg  (try --help)"; exit 2 ;;
    esac
done

echo "→ Checking the build interpreter"
if ! python3 -c "import tkinter" >/dev/null 2>&1; then
    echo "✗ This python3 has no tkinter, so the bundle would not run."
    echo "  python3 is: $(command -v python3)"
    echo "  macOS: install Python from python.org or 'brew install python-tk'."
    echo "  Debian/Ubuntu: sudo apt install python3-tk"
    exit 1
fi

echo "→ Cleaning previous build artifacts"
rm -rf build dist

echo "→ Installing build dependencies"
PYBIN="python3"
if ! python3 -m pip install --quiet --upgrade pyinstaller Pillow 2>/dev/null; then
    # Homebrew and Debian mark their Python "externally managed" (PEP 668),
    # so pip refuses to install into it.  Build from a local venv instead —
    # it inherits the same stdlib, tkinter included.
    echo "  (this Python is externally managed — building from .venv-build)"
    python3 -m venv .venv-build
    PYBIN="$HERE/.venv-build/bin/python"
    "$PYBIN" -m pip install --quiet --upgrade pip
    "$PYBIN" -m pip install --quiet --upgrade pyinstaller Pillow
fi

echo "→ Building bundle with PyInstaller"
"$PYBIN" -m PyInstaller CollectorCatalog.spec --noconfirm --log-level WARN

# ── Replace the copy the user actually launches ──────────────────────────────

replace_app_bundle() {
    # $1 = destination .app path.  Only ever removes our own bundle.
    local dest="$1" src="dist/$APP_NAME.app"
    if [[ -e "$dest" && "$(basename "$dest")" != "$APP_NAME.app" ]]; then
        echo "  ! Refusing to touch $dest — not our bundle"
        return 1
    fi
    rm -rf "$dest"
    cp -R "$src" "$dest"
    echo "  ✓ $dest"
}

install_macos() {
    local src="dist/$APP_NAME.app" found=0

    if pgrep -f "$APP_NAME.app/Contents/MacOS" >/dev/null 2>&1; then
        echo "✗ $APP_NAME is still running — quit it first, then re-run with --install."
        exit 1
    fi

    echo "→ Replacing the installed copy"
    for dest in "$HOME/Desktop/$APP_NAME.app" "/Applications/$APP_NAME.app"; do
        if [[ -e "$dest" ]]; then
            replace_app_bundle "$dest" && found=1
        fi
    done

    # Nothing installed yet — put it on the Desktop, which is where the
    # shortcut lives for this project.
    if [[ "$found" -eq 0 ]]; then
        replace_app_bundle "$HOME/Desktop/$APP_NAME.app"
        echo "  (no existing copy found, so it went to the Desktop)"
    fi

    # Clear the quarantine flag so the refreshed copy opens without the
    # right-click → Open dance every time.
    xattr -dr com.apple.quarantine "$HOME/Desktop/$APP_NAME.app" 2>/dev/null || true
    xattr -dr com.apple.quarantine "/Applications/$APP_NAME.app"  2>/dev/null || true
}

install_linux() {
    local target="$HERE/dist/CollectorCatalog/CollectorCatalog"
    local apps="$HOME/.local/share/applications"
    local desktop_file="$apps/collector-catalog.desktop"

    echo "→ Refreshing the launcher"
    mkdir -p "$apps"
    cat > "$desktop_file" <<EOF
[Desktop Entry]
Type=Application
Name=$APP_NAME
Comment=Universal collectables catalog
Exec=$target
Path=$HERE
Terminal=false
Categories=Office;Database;
EOF
    chmod +x "$desktop_file"
    echo "  ✓ $desktop_file"

    if [[ -d "$HOME/Desktop" ]]; then
        cp "$desktop_file" "$HOME/Desktop/collector-catalog.desktop"
        chmod +x "$HOME/Desktop/collector-catalog.desktop"
        echo "  ✓ $HOME/Desktop/collector-catalog.desktop"
    fi
    command -v update-desktop-database >/dev/null 2>&1 &&
        update-desktop-database "$apps" 2>/dev/null || true
}

if [[ "$(uname -s)" == "Darwin" ]]; then
    APP="dist/$APP_NAME.app"
    if [[ ! -d "$APP" ]]; then
        echo "✗ Build finished but no .app found in dist/"
        exit 1
    fi
    echo
    echo "✓ Built:  $APP"
    if [[ "$INSTALL" -eq 1 ]]; then
        install_macos
        echo
        echo "✓ Done — the copy you launch is now the current build."
    else
        echo "  Double-click it in Finder, or:  open \"$APP\""
        echo
        echo "  First launch on macOS:  right-click → Open  (Gatekeeper)"
        echo "  To replace the copy on your Desktop:  $0 --install"
    fi
else
    echo "✓ Built:  dist/CollectorCatalog/"
    if [[ "$INSTALL" -eq 1 ]]; then
        install_linux
    else
        echo "  To add/refresh a launcher for it:  $0 --install"
    fi
fi
