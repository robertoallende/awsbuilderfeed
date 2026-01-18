#!/bin/bash
# Install BuilderFeed systemd services

set -e

PROJECT_DIR="/home/rover/prefect/awsbuilderfeed"
SYSTEMD_DIR="/etc/systemd/system"

echo "Installing BuilderFeed systemd services..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo $0"
    exit 1
fi

# Copy service files
echo "Copying service files to $SYSTEMD_DIR..."
cp "$PROJECT_DIR/systemd/prefect-server.service" "$SYSTEMD_DIR/"
cp "$PROJECT_DIR/systemd/builderfeed.service" "$SYSTEMD_DIR/"

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable services
echo "Enabling services..."
systemctl enable prefect-server.service
systemctl enable builderfeed.service

# Start services
echo "Starting services..."
systemctl start prefect-server.service
sleep 5
systemctl start builderfeed.service

# Show status
echo ""
echo "=== Service Status ==="
systemctl status prefect-server.service --no-pager || true
echo ""
systemctl status builderfeed.service --no-pager || true

echo ""
echo "Installation complete!"
echo ""
echo "Useful commands:"
echo "  View status:    systemctl status prefect-server builderfeed"
echo "  View logs:      journalctl -u builderfeed -f"
echo "  Restart:        sudo systemctl restart builderfeed"
echo "  Stop all:       sudo systemctl stop builderfeed prefect-server"
echo ""
echo "Prefect UI available at: http://localhost:4200"
