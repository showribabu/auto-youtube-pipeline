#!/bin/bash
# Install auto-youtube-pipeline as a systemd service on a Linux host.
# Run from the repo root after copying it to /opt/auto-youtube-pipeline:
#   sudo bash scripts/install_service.sh
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="${INSTALL_DIR:-/opt/auto-youtube-pipeline}"

echo "Installing from: $SRC_DIR"
echo "Into:            $INSTALL_DIR"

# 1. Python venv
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# 2. Directories the pipeline writes to
mkdir -p "$INSTALL_DIR/output" "$INSTALL_DIR/logs" "$INSTALL_DIR/cache"

# 3. ffmpeg (the pipeline resolves it from PATH; this makes sure it is there)
if ! command -v ffmpeg >/dev/null 2>&1; then
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -qq && apt-get install -y ffmpeg
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y ffmpeg
    else
        echo "WARNING: install ffmpeg manually; the pipeline needs it on PATH."
    fi
fi

# 4. systemd unit
cp "$SRC_DIR/systemd/auto-youtube.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable auto-youtube.service
systemctl restart auto-youtube.service

echo "Installed. Follow it with:  journalctl -u auto-youtube -f"