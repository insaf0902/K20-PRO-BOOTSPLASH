#!/bin/sh
# Rebuild the boot logo and the flashable zip.
#   ./build.sh              -> out/RRSplash-raphael.zip
# Needs: python3 + Pillow, zip
set -e
cd "$(dirname "$0")"
mkdir -p out
python3 tools/make.py assets/source.png assets/rr_swoosh_mask.png assets/boot_logo_1080x2340.png
# slots 2 (fastboot) and 4 (system destroyed) are kept from the current cache/logo.img
cp cache/logo.img out/base.img
python3 tools/pack.py out/base.img assets/boot_logo_1080x2340.png cache/logo.img
rm -f out/base.img out/RRSplash-raphael.zip
zip -r -X -9 out/RRSplash-raphael.zip META-INF cache >/dev/null
echo "Built out/RRSplash-raphael.zip"
