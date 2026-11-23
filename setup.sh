#!/bin/sh
# Recreates the working layout the tests and tools expect, from this repo.
# Run once at the start of a session:  sh setup.sh
REPO="$(cd "$(dirname "$0")" && pwd)"
ln -sfn "$REPO" /home/claude/brand          # addons (tests read /home/claude/brand/<Addon>/...)
ln -sfn "$REPO/tools" /home/claude/tools    # test suite and art generators
ln -sfn "$REPO/mock" /home/claude/mock      # mockup scripts
mkdir -p /tmp/v4 && cp "$REPO/refs/f_057.png" /tmp/v4/f_057.png   # reference game frame for mockups
pip install --break-system-packages -q lupa pillow numpy opencv-python-headless fonttools luaparser 2>/dev/null
echo "Ready. Build the zip with:  cd /home/claude/brand && zip -qr9 /home/claude/AetherAddons.zip Aether*"
