# Unijoy Keyboard Layout

**Unijoy** (also called UniBijoy) is the standard Unicode-compatible Bangla keyboard layout used across Bangladesh. This repository packages it for Linux, Windows, and Android.

## What is Unijoy?

The widely-used Bijoy keyboard layout was designed for ASCII-based Bangla software and was never compatible with Unicode. To fix this, the [Ekushey Project](https://ekushey.org) developed Unijoy in 1999, a Unicode-native layout that preserves the familiar Bijoy key positions while working correctly with modern operating systems and applications. On 7 December 2005 it was incorporated into the m17n project database under the GNU Lesser General Public License.

### How Unijoy differs from Bijoy

While Unijoy keeps the same physical key positions as Bijoy, several things work differently because Unijoy is built on Unicode:

- **ো (o-kar) vs ও:** In Bijoy, a dedicated key types the letter ও. In Unijoy the same key types the vowel sign ো (o-kar), which is the correct Unicode representation.
- **Vowel sign ordering:** In Bijoy, you type e-kar and oi-kar *before* the consonant (an old convention). In Unijoy, all vowel signs are typed *after* the consonant, following Unicode's logical order.
- **ো and ৌ:** These combined vowel signs are absent from Bijoy because Bijoy assembles them from separate pieces. Unijoy includes them as proper Unicode characters.
- **Special Unicode characters:** Unijoy includes Zero-Width Joiner (ZWJ) and Zero-Width Non-Joiner (ZWNJ), which are sometimes needed to control how conjuncts form.

The Android layout has two additional differences from Bijoy:

- **Different positions for some characters:** The keys for daṛi (।), khaṇḍa ta (ৎ), bisarga (ঃ), and chandrabindu (ঁ) are in different positions from the original Bijoy layout.
- **No dedicated Reph key:** Bijoy reserves a key for Reph (the superscript form of র). The Android layout does not. Reph is produced by typing র followed by হসন্ত before the next consonant, which is how Unicode represents it.

## Platforms

| Platform | Method | Status |
|---|---|---|
| Linux (IBus/m17n) | Bundled in `m17n-db` (updated layout in ≥ 1.8.13) | No installation needed. See [m17n-db](https://cgit.git.savannah.nongnu.org/cgit/m17n/m17n-db.git/) |
| Linux (XKB) | Symbols file + XKB rules registration | See [XKB installation](#xkb-installation-linux) |
| Windows | Installer built with MSKLC | See [Windows](#windows) |
| Android | [HeliBoard](https://github.com/Helium314/HeliBoard/releases/latest), [FlorisBoard](https://github.com/florisboard/florisboard/releases/latest), [FUTO Keyboard](https://play.google.com/store/apps/details?id=org.futo.inputmethod.latin.playstore), [Simple Keyboard](https://play.google.com/store/apps/details?id=rkr.simplekeyboard.inputmethod) | Available separately. [See project website](https://unijoy.pages.dev/android/) |

## Linux

There are two ways to use Unijoy on Linux. **IBus/m17n is the recommended method** for most people: it requires no root access and supports the full set of Bengali conjunct characters (ligatures) such as Ya-phala and Ra-phala. XKB is an alternative for setups where IBus isn't available.

### IBus/m17n (recommended)

The Unijoy input method has been part of `m17n-db` for many years. Version 1.8.13 updated it to the current, modernised layout. There is nothing to copy or configure manually: just install the packages and enable the layout.

**1. Install the packages**

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install ibus ibus-m17n m17n-db

# Fedora
sudo dnf install ibus ibus-m17n m17n-db

# Arch Linux
sudo pacman -S ibus ibus-m17n m17n-db
```

> `m17n-db` 1.8.13 ships the updated Unijoy layout. Earlier versions include an older revision of the layout. To check which version your distribution provides, run `dpkg -l m17n-db` or `rpm -q m17n-db`. If you're on an older version, see [Older distributions](#older-distributions).

**2. Enable IBus**

Make sure IBus is running. On most modern desktops it starts automatically, but you can start it manually if needed:

```bash
ibus-daemon -drx
```

**3. Add the Unijoy input source**

Open **Settings → Keyboard → Add Input Sources**, search for **Bangla (Bangladesh) / Bangla (India)**, and select **Bangla (bn-unijoy (m17n))**.

That's it. Switch to it using your desktop's input-source shortcut (usually <kbd>Super</kbd>+<kbd>Space</kbd>) and start typing.

**4. Verify**

```bash
ibus list-engine | grep -i unijoy
```

You should see `m17n:bn:unijoy` in the output. If not, run `ibus restart` and try again.

---

### XKB installation (Linux)

XKB is the keyboard system built into X11 and Wayland. It's lightweight and works without IBus, but it cannot compose certain Bengali conjunct characters (Ya-phala, Ra-phala, Reph). Use the IBus method if you need those.

This method adds a standalone **"Bangla (Unijoy)"** layout to your system: it appears in the keyboard picker just like any other layout.

**Prerequisites:** `bash`, `python3`, and `sudo`. All three are standard on any Linux desktop.

**1. Clone this repository**

```bash
git clone https://github.com/OishikStudio/unijoy.git
cd unijoy
```

**2. Run the installer**

```bash
./install.sh
```

The installer will:

- Copy the `unijoy` symbols file to `/usr/share/X11/xkb/symbols/`
- Register the layout in the XKB rules files under `/usr/share/X11/xkb/rules/`: the `.xml` files (`evdev.xml`, `base.xml`) so it appears in the desktop input-source picker, and the `.lst` files (`evdev.lst`, `base.lst`) so `localectl` and `setxkbmap` see it too

The rules files are edited in place. `./uninstall.sh` reverses the exact change (see [Uninstalling](#uninstalling)).

**3. Enable the layout**

Log out and back in, then open **Settings → Region & Language → Input Sources**, click **+**, search for **Bangla**, and add **Bangla (Unijoy)**.

#### Manual XKB steps

If you prefer to do it yourself rather than running the script, here is exactly what the installer does:

```bash
# Step 1: Copy the symbols file
sudo cp unijoy /usr/share/X11/xkb/symbols/unijoy

# Step 2: Register the layout in the XKB rules files
sudo python3 scripts/manage_xkb_variant.py install scripts/evdev-fragment.xml /usr/share/X11/xkb/rules
```

`manage_xkb_variant.py install` makes the smallest possible change, in place, to every rules file in the directory (skipping the `xorg.*` symlinks so their targets aren't edited twice): it adds Unijoy as a variant in two layouts, `bd` (Bangladesh) and `in` (India), in both registries. The `.xml` files (`evdev.xml`, `base.xml`) feed the desktop input-source picker, and the `.lst` files (`evdev.lst`, `base.lst`) feed `localectl` and `setxkbmap`. Editing only the `.xml` files is a common mistake: the layout then shows up in Settings but stays invisible to `localectl list-x11-keymap-variants`. The script is safe to run multiple times: it does nothing if the entries are already present.

Uninstalling reverses this exactly: `manage_xkb_variant.py uninstall` removes the same variant entries from every rules file in place (see [Uninstalling](#uninstalling)).

In the `.lst` files it adds two lines (alongside the Probhat ones):

```
  unijoy          bd: Bangla (Unijoy)
  ben_unijoy      in: Bangla (India, Unijoy)
```

In the `.xml` files it adds two `<variant>` blocks:

```xml
<!-- Added to the 'bd' (Bangladesh) layout, after probhat -->
<variant>
  <configItem>
    <name>unijoy</name>
    <shortDescription>bn</shortDescription>
    <description>Bangla (Unijoy)</description>
    <languageList>
      <iso639Id>ben</iso639Id>
      <iso639Id>sat</iso639Id>
    </languageList>
  </configItem>
</variant>

<!-- Added to the 'in' (India) layout, after ben_probhat -->
<variant>
  <configItem>
    <name>ben_unijoy</name>
    <shortDescription>bn</shortDescription>
    <description>Bangla (India, Unijoy)</description>
    <languageList>
      <iso639Id>ben</iso639Id>
      <iso639Id>sat</iso639Id>
    </languageList>
  </configItem>
</variant>
```

> **Why not replace the rules files wholesale?** They are maintained by your distribution and their contents differ between distros and versions. Replacing any of them wholesale can silently remove layouts you rely on or conflict with future package updates. The merge script edits only what needs to change.

#### XKB verification

```bash
# Confirm the variants are registered under the bd and in layouts.
# localectl reads the .lst files, so seeing 'unijoy' here proves the
# .lst registration worked (not just the .xml picker entry).
localectl list-x11-keymap-variants bd | grep unijoy
localectl list-x11-keymap-variants in | grep unijoy

# Preview the key map (requires the gkbd-capplet package)
gkbd-keyboard-display -l unijoy
```

---

### Uninstalling

```bash
./uninstall.sh
```

This removes the `unijoy` symbols file and removes the `unijoy`/`ben_unijoy` variant entries from every XKB rules file (`evdev.xml`, `base.xml`, `evdev.lst`, `base.lst`) in place, leaving the rest of those files untouched. Then remove **Bangla (Unijoy)** from **Settings → Region & Language → Input Sources**.

To remove the IBus method, simply remove the packages:

```bash
sudo apt remove ibus-m17n   # or the equivalent for your distro
```

#### Manual uninstall

```bash
sudo rm /usr/share/X11/xkb/symbols/unijoy
sudo python3 scripts/manage_xkb_variant.py uninstall scripts/evdev-fragment.xml /usr/share/X11/xkb/rules
```

---

### Older distributions

Unijoy has been part of `m17n-db` for many years, so the IBus method will work on virtually any distribution. However, if your distribution ships `m17n-db` older than 1.8.13, you will get an earlier revision of the layout rather than the current, updated one. You can check your installed version with:

```bash
# Debian / Ubuntu
dpkg -l m17n-db

# Fedora / RHEL
rpm -q m17n-db
```

You can also confirm that the input method file is present:

```bash
ls /usr/share/m17n/bn-unijoy.mim
```

If you're on an older version, you have two options:

1. **Wait for your distribution to update the package**, or build `m17n-db` from source.
2. **Download the updated `.mim` file directly** and drop it in place, without touching the rest of your `m17n-db` installation:

```bash
sudo curl -L -o /usr/share/m17n/bn-unijoy.mim \
  https://cgit.git.savannah.nongnu.org/cgit/m17n/m17n-db.git/plain/MIM/bn-unijoy.mim
```

Restart IBus afterward for the change to take effect:

```bash
ibus restart
```

> This replaces only `bn-unijoy.mim` with the current upstream version. The rest of your distribution's `m17n-db` package is left untouched. A future package upgrade may overwrite this file with the distro's (possibly older) version. If that happens, just re-run the command above.

---

### Troubleshooting

**Unijoy doesn't appear in the input source list after installing**
Log out and back in. Some desktops cache the keyboard registry per session. On GNOME (X11 only), you can also try pressing <kbd>Alt</kbd>+<kbd>F2</kbd>, typing `r`, and pressing <kbd>Enter</kbd> to restart the shell without logging out.

**IBus is installed but "Bangla (bn-unijoy (m17n))" isn't in the list**
Run `ibus list-engine | grep -i unijoy`. If the engine doesn't appear, confirm that `m17n-db` and `ibus-m17n` are both installed and run `ibus restart`. Note that on `m17n-db` older than 1.8.13 the engine will be present but will use an earlier revision of the layout (see [Older distributions](#older-distributions)).

**Switching to Unijoy does nothing / I still get English**
Confirm IBus is actually running: `pgrep ibus-daemon`. If not, start it with `ibus-daemon -drx`. Also make sure the *active* input source in the system tray shows the IBus Unijoy engine, not a plain XKB layout.

**Bengali text shows as boxes or question marks**
This is a missing font, not a layout problem. Install a font with full Bengali Unicode coverage:

```bash
sudo apt install fonts-noto-core                  # Debian / Ubuntu: core Noto weights, includes Bengali
sudo apt install fonts-noto                       # Debian / Ubuntu: pulls in the full Noto family, including Bengali
sudo dnf install google-noto-sans-bengali-fonts   # Fedora
```

**Conjuncts (Ya-phala, Ra-phala, etc.) don't form correctly**
The XKB layout cannot compose conjunct characters. This is a known limitation of XKB. Switch to the **IBus/m17n** method, which handles all conjuncts correctly.

**`manage_xkb_variant.py` can't find the rules files**
Your distribution may place them in a slightly different location. Find the directory with:

```bash
find /usr/share/X11/xkb/rules -name 'evdev.*'
```

Pass the correct directory to the script manually:

```bash
sudo python3 scripts/manage_xkb_variant.py install scripts/evdev-fragment.xml /path/to/xkb/rules
```

---

### Compatibility

- **X11 and Wayland:** Both methods work on both display servers. On Wayland, the input-source list is managed entirely by the desktop environment (via `gsettings`/`dconf` on GNOME), so the XKB layout will appear there once the rules files are updated.
- **Desktop environments:** Instructions reference GNOME's Settings app. KDE Plasma, XFCE, MATE, and others expose the same underlying IBus engines and XKB layouts through their own keyboard or input-method settings panels.
- **Package upgrades:** `install.sh` does not touch the XKB rules files wholesale, so a distribution upgrade is unlikely to revert the changes. However, if `xkeyboard-config` is upgraded, it may overwrite them. In that case, re-run `install.sh`.

---

## Windows

A Windows installer built with [MSKLC (Microsoft Keyboard Layout Creator)](https://www.microsoft.com/en-us/download/details.aspx?id=102134) is included in release. Download and run it to install the Unijoy layout on Windows 10 or 11.

**1. Download the installer**

Download `unijoy-windows-installer.zip` from the [latest release](https://github.com/OishikStudio/unijoy/releases/latest/download/unijoy-windows-installer.zip).

**2. Extract and run**

Extract the zip, then run `setup.exe` inside it (administrator rights are required). It may show a SmartScreen "unrecognized app" warning since the installer isn't code-signed; click **More info → Run anyway** to proceed. Windows may show a **User Account Control (UAC)** prompt asking for permission, click **Yes**. 

**3. Switch to it**

Once installed, use the language bar in the taskbar (or <kbd>Win</kbd>+<kbd>Space</kbd>) to switch to **Bangla (Unijoy)**.

<sub>The installer normally adds the Bangla language and Unijoy keyboard automatically. If it doesn't, add it manually via **Settings → Time & Language → Language & Region → Add a language**, and choose **Bangla (Unijoy)**.</sub>

The zip also includes two reference PDFs to help you get started:

- **[user-manual.pdf](docs/manuals/user-manual.pdf)**: how to use the layout for typing once it's installed.
- **[bangla-ligature-list.pdf](docs/manuals/bangla-ligature-list.pdf)**: the full list of Bangla conjuncts (ligatures) and how to type them.

**Uninstalling**

Run `setup.exe` again and choose the `Remove the keyboard layout` option, or remove it from **Settings → Apps → Installed apps** by searching for "Unijoy".

**Note: VIRAMA key differs from Linux/m17n**

The `g`/`G` (hasanta/VIRAMA) keys behave differently on Windows than in the m17n `.mim` file:

| Input | Windows | m17n (Linux) |
|---|---|---|
| g |  ্ (VIRAMA dead key) |  ্ (VIRAMA dead key) |
| G | । (Danda) | । (Danda) |
| VIRAMA (dead key) + VIRAMA (g + g) | ্ (VIRAMA) | ্‌ (VIRAMA + ZWNJ) |
| VIRAMA (dead key) + Danda (g + G) | ॥ (Double Danda) | ॥ (Double Danda) |
| Alt+g | ্‌ (VIRAMA + ZWNJ) | ্ (VIRAMA) |
| Alt+G | ॥ (Double Danda) | ্‌ (VIRAMA + ZWNJ) |

---

## Project structure

```
.
├── README.md                            # This file
├── docs/
│   └── manuals/                         # User Manual, Bangla Ligature List (ODT + PDF)
│       ├── user-manual.odt
│       ├── user-manual.pdf
│       ├── bangla-ligature-list.odt
│       └── bangla-ligature-list.pdf
├── unijoy                               # XKB symbols file (Linux)
├── unijoy.klc                           # MSKLC keyboard layout file (Windows)
├── install.sh                           # XKB installer (Linux, needs sudo)
├── uninstall.sh                         # Reverses install.sh
└── scripts/
    ├── manage_xkb_variant.py            # In-place install/uninstall of the unijoy variants
    └── evdev-fragment.xml               # The two <variant> blocks to insert/remove
```

---

## License

GNU General Public License v3.0. See [LICENSE](LICENSE) for details.
