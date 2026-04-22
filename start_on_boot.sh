#!/bin/bash
# Place this file in /home/pi/tello-mapper/
# Register with: crontab -e  →  @reboot /home/pi/tello-mapper/start_on_boot.sh

sleep 30  # Wait for Wi-Fi to associate with Tello
cd /home/pi/tello-mapper
source venv/bin/activate
python3 main.py --auto-start
