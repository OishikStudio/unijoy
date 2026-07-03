#!/usr/bin/env bash
#
# install.sh -- Install the Unijoy Bangla keyboard layout on Linux (XKB).
#
# Two steps, both need sudo:
#   1. Copy the 'unijoy' symbols file to /usr/share/X11/xkb/symbols/
#   2. Register it in the XKB rules files so it appears everywhere: the .xml
#      files (evdev.xml/base.xml) feed the desktop input-source picker, and
#      the .lst files (evdev.lst/base.lst) feed localectl and setxkbmap.
#
# The rules files are edited in place. Run uninstall.sh to reverse the change.
#
# Note: the IBus/m17n method needs no installation at all, just install
# ibus and ibus-m17n, then add Bengali (Unijoy) from Settings.
# See README.md for details.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

XKB_SYMBOLS_DIR="/usr/share/X11/xkb/symbols"
XKB_RULES_DIR="/usr/share/X11/xkb/rules"

bold()    { printf '\033[1m%s\033[0m\n' "$1"; }
success() { printf '\033[32m✓\033[0m %s\n' "$1"; }
info()    { printf '  %s\n' "$1"; }

confirm() {
    local reply
    read -r -p "$1 [Y/n] " reply || true
    case "$reply" in
        [nN]*) return 1 ;;
        *) return 0 ;;
    esac
}

check_prerequisites() {
    if [ ! -d "$XKB_SYMBOLS_DIR" ] || [ ! -d "$XKB_RULES_DIR" ]; then
        echo "error: XKB configuration not found at the expected paths:"
        echo "  $XKB_SYMBOLS_DIR"
        echo "  $XKB_RULES_DIR"
        echo
        echo "Locate your XKB rules directory with:"
        echo "  find /usr/share/X11/xkb/rules -name 'evdev.*'"
        echo "Then pass it to scripts/manage_xkb_variant.py as the last argument."
        exit 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "error: python3 is required but was not found."
        exit 1
    fi
}

install_xkb() {
    bold "==> Installing Unijoy XKB layout (requires sudo)"
    check_prerequisites

    sudo cp -v "$REPO_DIR/unijoy" "$XKB_SYMBOLS_DIR/unijoy"
    success "Symbols file installed."

    sudo python3 "$REPO_DIR/scripts/manage_xkb_variant.py" install \
        "$REPO_DIR/scripts/evdev-fragment.xml" \
        "$XKB_RULES_DIR"
    success "XKB rules files updated in place."
}

main() {
    bold "Unijoy Layout: XKB Installer"
    echo
    echo "This installs the Unijoy XKB keyboard layout system-wide."
    echo "It will ask for your sudo password."
    echo
    echo "Note: if you plan to use Unijoy via IBus/m17n (recommended),"
    echo "you do NOT need to run this installer. Just install ibus and"
    echo "ibus-m17n, then add 'Bengali (Unijoy (m17n))' in Settings."
    echo "See README.md for details."
    echo

    if ! confirm "Continue with XKB installation?"; then
        echo "Aborted."
        exit 0
    fi

    install_xkb

    echo
    bold "Done!"
    echo
    echo "Next steps:"
    echo "  1. Log out and back in (or restart your session)."
    echo "  2. Open Settings → Region & Language → Input Sources."
    echo "  3. Click '+', search for 'Bangla', and add 'Bangla (Unijoy)'."
    echo
    echo "To remove this layout, run: ./uninstall.sh"
}

main "$@"
