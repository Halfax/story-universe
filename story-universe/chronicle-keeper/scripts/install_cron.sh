#!/bin/sh
set -e

# Installer: copies cron/chronicle-keeper into /etc/cron.d/
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$SRC_DIR/cron/chronicle-keeper"
DEST="/etc/cron.d/chronicle-keeper"

if [ ! -f "$SRC" ]; then
  echo "Source cron file not found: $SRC" >&2
  exit 1
fi

echo "Installing $DEST (requires sudo)"
sudo cp "$SRC" "$DEST"
sudo chmod 644 "$DEST"
sudo chown root:root "$DEST"

echo "Ensure the startup script is executable:" 
echo "  sudo chmod +x $SRC_DIR/scripts/start_on_boot.sh"

echo "Reloading cron service if available..."
if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl restart cron || sudo systemctl restart crond || true
else
  sudo service cron restart || true
fi

echo "Installed $DEST"
