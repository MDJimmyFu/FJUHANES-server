# Hospital Login Automation - Implementation Plan

## Goal Description
Design and implement a Python-based tool that allows a user to enter their credentials once and automatically logs them into:
1.  **Inpatient Web System**: A web-based application (using Playwright).
2.  **Hospital HIS**: A desktop application (using `pywinauto` or similar, or just launching it if automation is too complex without access).

## User Review Required
> [!NOTE]
> **Configuration**:
> - **Web System**: `http://10.10.246.80/Ipo/HISLogin`
> - **HIS System**: `C:\VGHTC\HISLogin.exe`

> [!WARNING]
> **Security**: Storing passwords or handling them in plain text can be risky. This tool will accept passwords in memory for the session.

## Proposed Changes

### Project Structure
`C:\Users\A03772\.gemini\antigravity\scratch\hospital_login_tool\`
- `main.py`: Entry point, GUI for login.
- `web_login.py`: Handles browser automation (Playwright).
- `his_login.py`: Handles desktop application automation (Pywinauto).
- `config.py`: Configuration for URLs and paths.
- `requirements.txt`: Dependencies.

### Dependencies
- `playwright`: For robust web automation.
- `tk` (Standard library): For the simple GUI.
- `pywinauto` (Optional): For desktop app interaction if needed.

## Verification Plan
### Automated Tests
- None possible without access to the real systems.
### Manual Verification
- Run `main.py`.
- Enter dummy credentials.
- Verify browser launches and attempts to type into placeholder fields.
- Verify "HIS" stub prints actions to console.
