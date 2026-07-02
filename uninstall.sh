#!/usr/bin/env bash
#
# uninstall.sh -- Reverse everything install.sh did.
#
# Removes the 'unijoy' XKB symbols file and removes the 'unijoy'/'ben_unijoy'
# variant entries from the XKB rules files (evdev.xml/base.xml and
# evdev.lst/base.lst) in place, leaving the rest of those files untouched.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

XKB_SYMBOLS_DIR="/usr/share/X11/xkb/symbols"
XKB_RULES_DIR="/usr/share/X11/xkb/rules"

bold()    { printf '\033[1m%s\033[0m\n' "$1"; }
success() { printf '\033[32m✓\033[0m %s\n' "$1"; }

remove_xkb() {
    bold "==> Removing Unijoy XKB layout (requires sudo)"

    if [ -f "$XKB_SYMBOLS_DIR/unijoy" ]; then
        sudo rm -v "$XKB_SYMBOLS_DIR/unijoy"
        success "Symbols file removed."
    else
        echo "Nothing to remove ($XKB_SYMBOLS_DIR/unijoy not found)."
    fi

    if [ -d "$XKB_RULES_DIR" ]; then
        sudo python3 "$REPO_DIR/scripts/manage_xkb_variant.py" uninstall \
            "$REPO_DIR/scripts/evdev-fragment.xml" \
            "$XKB_RULES_DIR"
        success "XKB rules files updated in place."
    else
        echo "XKB rules directory not found at $XKB_RULES_DIR; nothing to update there."
    fi
}

main() {
    bold "Unijoy Layout — Uninstaller"
    echo

    remove_xkb

    echo
    bold "Done!"
    echo
    echo "If 'Bangla (Unijoy)' is still listed under"
    echo "Settings → Region & Language → Input Sources,"
    echo "remove it from there as well."
}

main "$@"
