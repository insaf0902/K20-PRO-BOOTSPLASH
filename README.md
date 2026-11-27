# Redmi K20 Pro Bootsplash — Resurrection Remix

Custom boot logo for the **Redmi K20 Pro / Mi 9T Pro (`raphael`)**, flashable from TWRP / OrangeFox.

<p align="center"><img src="assets/preview.png" width="300" alt="Boot logo preview"></p>

- Silver Resurrection Remix "double swoosh" logo with `#GETRESURRECTED`
- Small outline "unlocked" padlock at the top, like the stock Redmi unlocked boot screen
- Stock-style **Powered by android** lockup with the green robot head at the bottom
- Shown on normal boot **and** on unlocked-bootloader boot (no "unlocked" warning screen)
- Fastboot and "system destroyed" screens stay stock

> ⚠️ **Only for raphael.** The installer refuses to flash on any other device.

## Download

Get **`RRSplash-Raphael.zip`** from the [latest release](https://github.com/insaf0902/K20-PRO-BOOTSPLASH/releases/latest).

## Install

1. [Download](https://github.com/insaf0902/K20-PRO-BOOTSPLASH/releases/latest) `RRSplash-Raphael.zip`, or build it yourself (see below).
2. Boot into TWRP / OrangeFox and flash the zip.
3. Reboot.

The installer:

1. checks that the device is `raphael`
2. finds the `logo` partition (`/dev/block/by-name/logo` or `/dev/block/bootdevice/by-name/logo`)
3. checks the image fits the partition
4. backs up your current logo to `/sdcard/logo_backup.img` (once; never overwrites an existing backup)
5. writes the new logo and reads it back to verify

### Restore stock

```sh
fastboot flash logo logo_backup.img
```

or flash `logo.img` from the official MIUI fastboot ROM.

## Build

Requirements: `python3` with Pillow and `zip`. The Poppins font is bundled in `assets/fonts/`.

```sh
./build.sh            # -> out/RRSplash-raphael.zip
```

You can also zip it by hand: `zip -r RRSplash-raphael.zip META-INF cache`.

## Repository layout

| Path | Contents |
|---|---|
| `META-INF/com/google/android/update-binary` | Installer: shell script with busybox attached (from topjohnwu's Magisk) |
| `META-INF/com/google/android/updater-script` | Install logic (device check, backup, flash, verify) |
| `cache/logo.img` | Ready-to-flash `logo` partition image |
| `assets/source.png` | Original artwork (`#GETRESURRECTED`) |
| `assets/rr_swoosh.svg` | Resurrection Remix logo (from Simple Icons) |
| `assets/rr_swoosh_mask.png` | The SVG rendered to 1200×1200 (`tools/render_svg.js`) |
| `assets/boot_logo_1080x2340.png` | Final boot picture |
| `assets/fonts/Poppins-*.ttf` | Poppins font (SIL OFL 1.1, see `OFL-Poppins.txt`) |
| `tools/make.py` | Composes the 1080×2340 boot picture |
| `tools/pack.py` | Writes the picture into slots 1 and 3 of `logo.img` |
| `tools/render_svg.js` | Renders the SVG with Playwright/Chromium |

## `logo.img` format

Xiaomi `LOGO!!!!` format: zeros up to `0x4000`, then the magic `LOGO!!!!` followed by
(offset, length) pairs counted in 4 KiB blocks. Each slot holds an uncompressed 24-bit BMP.

| Slot | Offset | Size | Screen |
|---|---|---|---|
| 1 | `0x5000` | 1080×2340 | Boot logo |
| 2 | `0x740000` | 1080×1920 | Fastboot (stock) |
| 3 | `0xD2F000` | 1080×2340 | Boot logo, unlocked bootloader |
| 4 | `0x146A000` | 1080×1920 | "The system has been destroyed" (stock) |

## Credits

- Resurrection Remix logo: Resurrection Remix OS, via [Simple Icons](https://simpleicons.org/). No license is
  stated for this icon; it belongs to the Resurrection Remix project.
- The Android robot is reproduced or modified from work created and shared by Google and used according
  to terms described in the [Creative Commons 3.0 Attribution License](https://creativecommons.org/licenses/by/3.0/).
  Android is a trademark of Google LLC.
- [Poppins](https://fonts.google.com/specimen/Poppins) font: The Poppins Project Authors, SIL Open Font License 1.1.
- Installer `update-binary` and busybox: topjohnwu (Magisk).
- Based on the original EvoSplash zip for raphael.
