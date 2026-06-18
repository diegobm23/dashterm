#!/usr/bin/env bash
# dashterm installer
# Usage: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"
TARGET="$INSTALL_DIR/dashterm"

echo ""
echo "  ╭─────────────────────────────────╮"
echo "  │       dashterm  installer       │"
echo "  ╰─────────────────────────────────╯"
echo ""

# Build the single-file executable (pure stdlib zipapp — no pip needed)
echo "  Building dashterm…"
bash "$SCRIPT_DIR/build.sh"

# Create ~/.local/bin if needed and install the built executable
mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/dist/dashterm" "$TARGET"
chmod +x "$TARGET"

echo "  ✓ Installed to $TARGET"
echo ""

# Check if ~/.local/bin is on PATH
_needs_path_fix=0
if ! echo "$PATH" | grep -qF "$INSTALL_DIR"; then
    _needs_path_fix=1
    _suggested_rc="$HOME/.zshrc"
    [[ "$SHELL" == */bash ]] && _suggested_rc="$HOME/.bashrc"
    [[ "$SHELL" == */fish ]] && _suggested_rc="$HOME/.config/fish/config.fish"
    echo "  ⚠️  $INSTALL_DIR is not on your PATH."
    echo "     Add this to your $_suggested_rc:"
    echo ""
    if [[ "$SHELL" == */fish ]]; then
        echo '     fish_add_path $HOME/.local/bin'
    else
        echo '     export PATH="$HOME/.local/bin:$PATH"'
    fi
    echo ""
fi

# Offer to add shell hook
echo "  ─────────────────────────────────────────────"
echo "  Add dashterm to your shell startup? (shows"
echo "  the dashboard every time you open a terminal)"
echo ""
read -r -p "  Shell: [1] bash  [2] zsh  [3] fish  [4] skip: " choice

add_hook() {
    local rcfile="$1"
    local hook='# dashterm — terminal dashboard'$'\n''dashterm'
    if [ "$_needs_path_fix" -eq 1 ] && ! grep -qF "$INSTALL_DIR" "$rcfile" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rcfile"
        echo "  ✓ Added $INSTALL_DIR to PATH in $rcfile"
    fi
    if grep -q "dashterm" "$rcfile" 2>/dev/null; then
        echo "  ✓ Hook already present in $rcfile"
    else
        echo "" >> "$rcfile"
        echo "$hook" >> "$rcfile"
        echo "  ✓ Hook added to $rcfile"
    fi
}

add_hook_fish() {
    local rcfile="$HOME/.config/fish/config.fish"
    mkdir -p "$(dirname "$rcfile")"
    if [ "$_needs_path_fix" -eq 1 ] && ! grep -qF "$INSTALL_DIR" "$rcfile" 2>/dev/null; then
        echo 'fish_add_path $HOME/.local/bin' >> "$rcfile"
        echo "  ✓ Added $INSTALL_DIR to PATH in $rcfile"
    fi
    if grep -q "dashterm" "$rcfile" 2>/dev/null; then
        echo "  ✓ Hook already present in $rcfile"
    else
        printf '\n# dashterm — terminal dashboard\ndashterm\n' >> "$rcfile"
        echo "  ✓ Hook added to $rcfile"
    fi
}

case "$choice" in
    1) add_hook "$HOME/.bashrc" ;;
    2) add_hook "$HOME/.zshrc"  ;;
    3) add_hook_fish ;;
    4) echo "  Skipped. You can add 'dashterm' manually to your shell rc file." ;;
    *) echo "  Skipped." ;;
esac

echo ""
echo "  ─────────────────────────────────────────────"
echo "  Run setup now to configure city & countdowns?"
echo ""
read -r -p "  [Y/n]: " run_setup
if [[ "$run_setup" != "n" && "$run_setup" != "N" ]]; then
    echo ""
    "$TARGET" --setup
else
    echo ""
    echo "  Done! Run:  dashterm --setup   to configure"
    echo "              dashterm           to view dashboard"
    echo "              dashterm --live    for live clock mode"
    echo ""
fi
