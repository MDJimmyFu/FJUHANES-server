# Plan to Combine Servers into One Executable

The goal is to bundle `SurgerySchedule` (scratch) and `AutoPrescribe_Portable` into a single standalone executable while maintaining them as two separate servers running on different ports.

## Proposed Changes

### [NEW] Combined Directory Structure
A new directory `Combined_Server` will be created to house both applications.

### [NEW] `main.py`
This script will serve as the entry point for the executable. It will:
1. Start the `SurgerySchedule` server on port 5000 in a separate thread/process.
2. Start the `AutoPrescribe` server on port 3000 in a separate thread/process.
3. (Optional) Open a browser to a simple landing page or the main application.

### [MODIFY] SurgerySchedule Component
- Move relevant files from `scratch` to `Combined_Server/SurgerySchedule/`.
- Adjust `resource_path` to handle the new directory structure.

### [MODIFY] AutoPrescribe Component
- Move relevant files from `AutoPrescribe_Portable` to `Combined_Server/AutoPrescribe/`.
- Adjust `get_resource_path` to handle the new directory structure.

### [NEW] `build_combined.py`
A unified build script using PyInstaller that:
- Includes all templates, static files, and binary dependencies from both apps.
- Configures `main.py` as the entry point.

## Verification Plan

### Automated Tests
- None available currently. I will rely on manual verification after building.

### Manual Verification
1. Run `python main.py` and verify:
   - `http://localhost:5000` serves the Surgery Schedule app.
   - `http://localhost:3000` serves the AutoPrescribe app.
2. Run `python build_combined.py` to generate the executable.
3. Run `dist/Combined_Server.exe` and verify both servers are accessible.
