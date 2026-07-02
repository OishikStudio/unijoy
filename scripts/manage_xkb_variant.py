#!/usr/bin/env python3
"""
manage_xkb_variant.py -- register or unregister the "unijoy" (Bangla) XKB
layout across an X11 keyboard rules directory, in place.

Why this exists
----------------
An XKB layout is described in *two* parallel registries inside
/usr/share/X11/xkb/rules/, and different tools read different ones:

  * evdev.xml / base.xml  -- the rich XML registry read by GUI pickers
    (GNOME Settings, gkbd-keyboard-display, anything using libxkbregistry).
  * evdev.lst / base.lst  -- the plain-text list read by `localectl` and
    `setxkbmap`.

Editing only the .xml files makes the layout appear in the desktop input
picker but leaves it invisible to `localectl list-x11-keymap-variants` and
to `setxkbmap ... -variant unijoy`. To be registered properly the variant
has to be added to both registries. This script edits all of them at once.

These files are large, distribution-maintained registries of every XKB
layout on the system. Replacing any of them wholesale is risky: different
distributions and versions ship different contents, and a full overwrite can
silently remove layouts you rely on or break a future package upgrade. So we
make the smallest possible in-place edit instead.

Unijoy is a *variant* of the Bangla layout, the same way Probhat is, so it
belongs alongside Probhat inside the existing 'bd' (Bangladesh) and 'in'
(India) layouts, not as a new standalone layout of its own.

What this script does
----------------------
install (default):
  For every real rules file in the directory (symlinks such as xorg.xml /
  xorg.lst are skipped so their targets aren't edited twice):
    * .xml -- inserts the <variant> block right after the 'probhat' /
      'ben_probhat' variant inside the 'bd' / 'in' <layout> blocks.
    * .lst -- inserts a "  <name>  <layout>: <description>" line right after
      the matching 'probhat' / 'ben_probhat' line in the '! variant' section.

uninstall:
  Removes exactly those entries again from every rules file, leaving
  everything else untouched.

All edits happen in place -- no backup file is created or required. Both
directions are idempotent: running either one again when there is nothing
left to do is a no-op.

Usage:
    sudo python3 manage_xkb_variant.py install   scripts/evdev-fragment.xml [rules-dir]
    sudo python3 manage_xkb_variant.py uninstall scripts/evdev-fragment.xml [rules-dir]

`rules-dir` defaults to /usr/share/X11/xkb/rules.
"""

import re
import sys
import pathlib

DEFAULT_RULES_DIR = "/usr/share/X11/xkb/rules"

# Which rules files to touch, in each registry. Symlinks among these
# (xorg.xml -> base.xml, xorg.lst -> base.lst) are skipped at runtime.
XML_FILES = ("evdev.xml", "base.xml")
LST_FILES = ("evdev.lst", "base.lst")

# The two variants we manage. `marker` selects the block in the fragment
# file; `layout`/`after` place it beside the existing Probhat variant.
VARIANTS = (
    {"marker": "BD-VARIANT", "layout": "bd", "after": "probhat"},
    {"marker": "IN-VARIANT", "layout": "in", "after": "ben_probhat"},
)


# --------------------------------------------------------------------------
# Fragment parsing
# --------------------------------------------------------------------------
def extract_fragment(fragment_text, marker):
    """Pull the <variant>...</variant> block between '<!-- marker -->' and
    '<!-- END marker -->' out of the fragment file."""
    pattern = re.compile(
        r"<!--\s*" + re.escape(marker) + r".*?-->\s*(.*?)\s*<!--\s*END\s*" + re.escape(marker) + r"\s*-->",
        re.S,
    )
    m = pattern.search(fragment_text)
    if not m:
        sys.exit(f"error: could not find '{marker}' block in fragment file")
    return m.group(1).strip()


def extract_tag(variant_block, tag):
    m = re.search(r"<" + tag + r">(.*?)</" + tag + r">", variant_block)
    if not m:
        sys.exit(f"error: could not read <{tag}> from fragment variant block")
    return m.group(1)


def parse_variants(fragment_text):
    """Return the VARIANTS list enriched with the name/description/xml block
    read from the fragment file."""
    parsed = []
    for spec in VARIANTS:
        block = extract_fragment(fragment_text, spec["marker"])
        parsed.append({
            **spec,
            "xml_block": block,
            "name": extract_tag(block, "name"),
            "description": extract_tag(block, "description"),
        })
    return parsed


# --------------------------------------------------------------------------
# .xml editing
# --------------------------------------------------------------------------
def find_layout_block(evdev_text, layout_name):
    pattern = re.compile(
        r"<layout>\s*<configItem>\s*<name>" + re.escape(layout_name) + r"</name>.*?</layout>",
        re.S,
    )
    return pattern.search(evdev_text)


def xml_insert_variant(text, layout_name, after_variant_name, variant_block, new_variant_name):
    """Insert variant_block right after the <variant> named after_variant_name,
    inside the layout named layout_name. No-op if new_variant_name is already
    present in that layout."""
    m = find_layout_block(text, layout_name)
    if not m:
        print(f"  (no '{layout_name}' layout here; skipped)")
        return text, False
    layout_block = m.group(0)

    if re.search(r"<name>" + re.escape(new_variant_name) + r"</name>", layout_block):
        return text, False

    variant_pattern = re.compile(
        r"([ \t]*)(<variant>\s*<configItem>\s*<name>" + re.escape(after_variant_name) + r"</name>.*?</variant>)",
        re.S,
    )
    vm = variant_pattern.search(layout_block)
    if not vm:
        print(f"  (no '{after_variant_name}' variant under '{layout_name}'; skipped)")
        return text, False

    # Reindent the fragment's lines (which use a 2-space relative indent) to
    # match the indentation of the sibling variant we're inserting after.
    indent = vm.group(1)
    indented_block = "\n".join(indent + line for line in variant_block.splitlines())

    new_layout_block = layout_block[: vm.end()] + "\n" + indented_block + layout_block[vm.end():]
    return text[: m.start()] + new_layout_block + text[m.end():], True


def xml_remove_variant(text, layout_name, variant_name):
    """Remove the <variant> named variant_name from the layout named
    layout_name, including the newline and indentation before it."""
    m = find_layout_block(text, layout_name)
    if not m:
        return text, False
    layout_block = m.group(0)

    variant_pattern = re.compile(
        r"\n[ \t]*<variant>\s*<configItem>\s*<name>" + re.escape(variant_name) + r"</name>.*?</variant>",
        re.S,
    )
    new_layout_block, count = variant_pattern.subn("", layout_block, count=1)
    if count == 0:
        return text, False
    return text[: m.start()] + new_layout_block + text[m.end():], True


# --------------------------------------------------------------------------
# .lst editing
# --------------------------------------------------------------------------
def lst_line(name, layout, description):
    """Format a variant line the same way xkeyboard-config does: two leading
    spaces, the name left-justified so the layout starts at column 18."""
    return "  " + name.ljust(16) + layout + ": " + description


def lst_insert_variant(text, layout, after_variant, new_name, description):
    """Insert a variant line right after the matching after_variant line in
    the '! variant' section. No-op if new_name/layout is already listed."""
    if re.search(r"(?m)^[ \t]*" + re.escape(new_name) + r"[ \t]+" + re.escape(layout) + r":", text):
        return text, False

    pattern = re.compile(
        r"(?m)^[ \t]*" + re.escape(after_variant) + r"[ \t]+" + re.escape(layout) + r":.*$"
    )
    m = pattern.search(text)
    if not m:
        print(f"  (no '{after_variant} {layout}:' line here; skipped)")
        return text, False

    return text[: m.end()] + "\n" + lst_line(new_name, layout, description) + text[m.end():], True


def lst_remove_variant(text, layout, name):
    """Remove the variant line for name/layout, including its trailing
    newline."""
    pattern = re.compile(r"(?m)^[ \t]*" + re.escape(name) + r"[ \t]+" + re.escape(layout) + r":.*\n?")
    new_text, count = pattern.subn("", text, count=1)
    return new_text, count > 0


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def real_files(rules_dir, names):
    """Yield paths in rules_dir that exist and are not symlinks (so a
    symlink like xorg.xml -> base.xml isn't edited on top of its target)."""
    for name in names:
        path = rules_dir / name
        if not path.exists():
            continue
        if path.is_symlink():
            print(f"skipping {name} (symlink)")
            continue
        yield path


def process_file(path, variants, mode):
    text = path.read_text(encoding="utf-8")
    is_xml = path.suffix == ".xml"
    changed = False

    for v in variants:
        if mode == "install":
            if is_xml:
                text, did = xml_insert_variant(text, v["layout"], v["after"], v["xml_block"], v["name"])
            else:
                text, did = lst_insert_variant(text, v["layout"], v["after"], v["name"], v["description"])
        else:
            if is_xml:
                text, did = xml_remove_variant(text, v["layout"], v["name"])
            else:
                text, did = lst_remove_variant(text, v["layout"], v["name"])
        changed = changed or did

    if changed:
        path.write_text(text, encoding="utf-8")
        verb = "updated" if mode == "install" else "cleaned"
        print(f"{path.name}: {verb} in place.")
    else:
        print(f"{path.name}: already up to date. Nothing written.")
    return changed


def run(mode, fragment_path, rules_dir):
    variants = parse_variants(fragment_path.read_text(encoding="utf-8"))

    any_changed = False
    for path in real_files(rules_dir, XML_FILES + LST_FILES):
        any_changed = process_file(path, variants, mode) or any_changed

    if any_changed:
        action = "registered" if mode == "install" else "unregistered"
        names = ", ".join(v["name"] for v in variants)
        print(f"\nUnijoy variants ({names}) {action} in {rules_dir}.")
    else:
        print(f"\nNothing to change in {rules_dir}.")


def main():
    if len(sys.argv) not in (3, 4) or sys.argv[1] not in ("install", "uninstall"):
        sys.exit(f"Usage: {sys.argv[0]} <install|uninstall> <fragment.xml> [rules-dir]")

    mode = sys.argv[1]
    fragment_path = pathlib.Path(sys.argv[2])
    rules_dir = pathlib.Path(sys.argv[3] if len(sys.argv) == 4 else DEFAULT_RULES_DIR)

    if not fragment_path.is_file():
        sys.exit(f"error: {fragment_path} not found")
    if not rules_dir.is_dir():
        sys.exit(f"error: rules directory {rules_dir} not found")

    run(mode, fragment_path, rules_dir)


if __name__ == "__main__":
    main()
