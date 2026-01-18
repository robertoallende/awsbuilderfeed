#!/bin/bash
# Uninstall BuilderFeed systemd services

set -e

SYSTEMD_DIR="/etc/systemd/system"

echo "Uninstalling BuilderFeed systemd services..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo $0"
    exit 1
fi

# Stop services
echo "Stopping services..."
systemctl stop builderfeed.service 2>/dev/null || true
systemctl stop prefect-server.service 2>/dev/null || true

# Disable services
echo "Disabling services..."
systemctl disable builderfeed.service 2>/dev/null || true
systemctl disable prefect-server.service 2>/dev/null || true

# Remove service files
echo "Removing service files..."
rm -f "$SYSTEMD_DIR/prefect-server.service"
rm -f "$SYSTEMD_DIR/builderfeed.service"

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

echo ""
echo "Uninstallation complete!"
echo "Services have been stopped, disabled, and removed."
