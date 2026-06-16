#!/usr/bin/env bash
# dashterm installer
# Usage: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"
TARGET="$INSTALL_DIR/dashterm"

echo ""
echo "  ╭─────────────────────────────╮"
echo "  │   dashterm  installer       │"
echo "  ╰─────────────────────────────╯"
echo ""

# Create ~/.local/bin if needed
mkdir -p "$INSTALL_DIR"

# Copy the script
cp "$SCRIPT_DIR/dashterm.py" "$TARGET"
chmod +x "$TARGET"

# Ensure shebang is present (it is, but just in case)
head -1 "$TARGET" | grep -q "python3" || sed -i '1s|^|#!/usr/bin/env python3\n|' "$TARGET"

echo "  ✓ Installed to $TARGET"
echo ""

# Check if ~/.local/bin is on PATH
if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
    echo "  ⚠️  $INSTALL_DIR is not on your PATH."
    echo "     Add this to your ~/.bashrc or ~/.zshrc:"
    echo ""
    echo '     export PATH="$HOME/.local/bin:$PATH"'
    echo ""
fi

# Offer to add shell hook
echo "  ─────────────────────────────────────────────"
echo "  Add dashterm to your shell startup? (shows"
echo "  the dashboard every time you open a terminal)"
echo ""
read -r -p "  Shell: [1] bash  [2] zsh  [3] skip: " choice

add_hook() {
    local rcfile="$1"
    local hook='# dashterm — terminal dashboard'$'\n''dashterm'
    if grep -q "dashterm" "$rcfile" 2>/dev/null; then
        echo "  ✓ Hook already present in $rcfile"
    else
        echo "" >> "$rcfile"
        echo "$hook" >> "$rcfile"
        echo "  ✓ Hook added to $rcfile"
    fi
}

case "$choice" in
    1) add_hook "$HOME/.bashrc" ;;
    2) add_hook "$HOME/.zshrc"  ;;
    3) echo "  Skipped. You can add 'dashterm' manually to your shell rc file." ;;
    *) echo "  Skipped." ;;
esac

echo ""
echo "  ─────────────────────────────────────────────"
echo "  Run setup now to configure city & countdowns?"
echo ""
read -r -p "  [Y/n]: " run_setup
if [[ "$run_setup" != "n" && "$run_setup" != "N" ]]; then
    echo ""
    python3 "$TARGET" --setup
else
    echo ""
    echo "  Done! Run:  dashterm --setup   to configure"
    echo "              dashterm           to view dashboard"
    echo "              dashterm --live    for live clock mode"
    echo ""
fi
