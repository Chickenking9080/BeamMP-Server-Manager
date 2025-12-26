#!/bin/bash

# Get the current directory and user
DIR=$(pwd)
USER_NAME=$USER

echo "--- Setting up BeamMP Panel Autostart ---"

# Create the systemd service file
sudo tee /etc/systemd/system/beammp-panel.service <<EOF
[Unit]
Description=BeamMP Neon Management Panel
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable, and start the service
sudo systemctl daemon-reload
sudo systemctl enable beammp-panel.service
sudo systemctl start beammp-panel.service

echo "-----------------------------------------"
echo "DONE! Your panel is now running in the background."
echo "It will automatically start whenever the server reboots."
echo "Use 'sudo systemctl status beammp-panel' to check it."
echo "-----------------------------------------"
