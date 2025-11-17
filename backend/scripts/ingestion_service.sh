#!/bin/bash
# Systemd service script for automated data ingestion
# Place this in /etc/systemd/system/sauti-ingestion.service

# Activate virtual environment and run ingestion
cd /home/denis/SautiAI/backend
source venv/bin/activate
python scripts/automated_ingestion.py --mode continuous --interval 360

