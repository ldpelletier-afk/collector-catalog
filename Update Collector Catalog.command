#!/usr/bin/env bash
# Double-click this file to update Collector Catalog.
#
# It fetches the latest code, rebuilds the app, and replaces the copy on
# your Desktop. Nothing here needs typing — but the window stays open at
# the end so you can read what happened.

cd "$(dirname "$0")" || exit 1

APP_NAME="Collector Catalog"

say()  { printf "\n%s\n" "$*"; }
fail() {
    printf "\n✗ %s\n" "$*"
    printf "\nNothing was changed. The app you have now still works.\n"
    printf "\nPress any key to close this window..."
    read -n 1 -s -r
    echo
    exit 1
}

printf "─────────────────────────────────────────────\n"
printf "  Updating %s\n" "$APP_NAME"
printf "─────────────────────────────────────────────\n"

# ── Checks ───────────────────────────────────────────────────────────────────
command -v git >/dev/null 2>&1 || fail \
"git isn't installed.
  Open Terminal, type  git  and press return — macOS will offer to
  install the Command Line Tools. Then run this again."

[ -d .git ] || fail \
"This script isn't sitting in the Collector Catalog source folder.
  Keep it inside the folder it came with (the one containing app.py)."

# ── Quit the app if it's running, so its files can be replaced ───────────────
if pgrep -f "$APP_NAME.app/Contents/MacOS" >/dev/null 2>&1; then
    say "→ $APP_NAME is open. Quitting it first (unsaved edits are saved)."
    osascript -e "quit app \"$APP_NAME\"" >/dev/null 2>&1
    for _ in $(seq 1 20); do
        pgrep -f "$APP_NAME.app/Contents/MacOS" >/dev/null 2>&1 || break
        sleep 0.5
    done
    if pgrep -f "$APP_NAME.app/Contents/MacOS" >/dev/null 2>&1; then
        fail "$APP_NAME wouldn't quit. Close it yourself, then run this again."
    fi
fi

# ── Get the latest code ──────────────────────────────────────────────────────
say "→ Fetching the latest version"
git fetch origin 2>&1 | sed 's/^/  /' || fail \
"Couldn't reach GitHub. Check your internet connection and try again."

before="$(git rev-parse HEAD 2>/dev/null)"
branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"

# Prefer main — that's where finished work lands.
if [ "$branch" != "main" ]; then
    if git checkout main >/dev/null 2>&1; then
        branch="main"
    else
        say "  (staying on '$branch' — couldn't switch to main)"
    fi
fi

git pull --ff-only origin "$branch" 2>&1 | sed 's/^/  /'
if [ "${PIPESTATUS[0]}" -ne 0 ]; then
    fail "Couldn't update the code.
  If you've edited files in this folder, move them aside and try again."
fi

after="$(git rev-parse HEAD 2>/dev/null)"
if [ "$before" = "$after" ]; then
    say "→ Already up to date — rebuilding anyway so the app matches."
else
    say "→ What's new:"
    git log --oneline --no-merges "$before..$after" 2>/dev/null |
        sed 's/^[0-9a-f]* /  • /' | head -20
fi

# ── Rebuild and install ──────────────────────────────────────────────────────
say "→ Building (this takes a minute or two)"
if ! ./build_app.sh --install; then
    fail "The build didn't finish. The messages above say why."
fi

printf "\n─────────────────────────────────────────────\n"
printf "  ✓ Done — %s is up to date.\n" "$APP_NAME"
printf "    Open it from your Desktop as usual.\n"
printf "─────────────────────────────────────────────\n"
printf "\nPress any key to close this window..."
read -n 1 -s -r
echo
