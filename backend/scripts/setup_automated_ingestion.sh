#!/bin/bash
# Setup script for automated data ingestion
# This creates a systemd service for continuous data ingestion

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "Setting up automated data ingestion..."

# Make scripts executable
chmod +x "$SCRIPT_DIR/automated_ingestion.py"
chmod +x "$SCRIPT_DIR/ingestion_service.sh"

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/sauti-ingestion.service"
if [ -f "$SERVICE_FILE" ]; then
    echo "Service file already exists. Backing up..."
    sudo cp "$SERVICE_FILE" "${SERVICE_FILE}.backup"
fi

echo "Creating systemd service..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Sauti AI Automated Data Ingestion
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin"
ExecStart=$BACKEND_DIR/venv/bin/python $SCRIPT_DIR/automated_ingestion.py --mode continuous --interval 360
Restart=always
RestartSec=10
StandardOutput=append:$BACKEND_DIR/ingestion.log
StandardError=append:$BACKEND_DIR/ingestion.log

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created at $SERVICE_FILE"
echo ""
echo "To start the service:"
echo "  sudo systemctl start sauti-ingestion"
echo ""
echo "To enable on boot:"
echo "  sudo systemctl enable sauti-ingestion"
echo ""
echo "To check status:"
echo "  sudo systemctl status sauti-ingestion"
echo ""
echo "To view logs:"
echo "  journalctl -u sauti-ingestion -f"
echo "  or"
echo "  tail -f $BACKEND_DIR/ingestion.log"

