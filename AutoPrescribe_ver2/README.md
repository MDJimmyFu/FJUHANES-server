# AutoPrescribe Portable Package

This folder contains everything needed to run the AutoPrescribe application on another computer.

## Contents
- `app.py`: The web application server.
- `his_client.py`: HIS system integration client.
- `templates/`: UI templates.
- `Ipo/`: Data templates for prescriptions.
- `requirements.txt`: Python dependencies.
- `start.sh`: Launch script for macOS/Linux.
- `start.bat`: Launch script for Windows.

## Instructions

### On macOS/Linux
1. Open Terminal.
2. Navigate to this folder.
3. Run: `./start.sh`

### On Windows
1. Double-click `start.bat`.

The application will be available at `http://localhost:3000`.
