# Packaging Implementation Plan

This plan outlines the steps to package the `AutoPrescribe_Portable` Flask application into a single, standalone Windows executable (`.exe`).

## Proposed Changes

### Core Infrastructure

#### [NEW] [utils.py](file:///c:/Users/A03772/.gemini/antigravity/AutoPrescribe_Portable/utils.py)
- Implement `get_resource_path(relative_path)` to resolve file paths correctly whether running as a script or as a bundled executable.

### Application Updates

#### [MODIFY] [app.py](file:///c:/Users/A03772/.gemini/antigravity/AutoPrescribe_Portable/app.py)
- Import `get_resource_path` from `utils.py`.
- Configure Flask to use the bundled `templates` folder via `get_resource_path`.
- Update the PDF download route to use `get_resource_path` for locating `Controlled_Drug_Sheet_P022.pdf`.

#### [MODIFY] [his_client.py](file:///c:/Users/A03772/.gemini/antigravity/AutoPrescribe_Portable/his_client.py)
- Import `get_resource_path` from `utils.py`.
- Update all file reading operations (JSON templates) and file writing operations (PDF download) to use `get_resource_path`.

### Build Automation

#### [NEW] [build.py](file:///c:/Users/A03772/.gemini/antigravity/AutoPrescribe_Portable/build.py)
- Create a Python script to run PyInstaller with the necessary flags:
  - `--onefile`: Bundle into a single EXE.
  - `--add-data`: Include `templates/` and `Ipo/` folders.
  - `--name`: Set the output name to `AutoPrescribe.exe`.
  - `--noconsole`: (Optional) Disable the console window if desired. I will keep the console for now for easier debugging unless you prefer otherwise.

## Verification Plan

### Manual Verification
1. **Install PyInstaller**: Run `pip install pyinstaller`.
2. **Build**: Run `python build.py`.
3. **Test Executable**:
   - Locate `dist/AutoPrescribe.exe`.
   - Run it and verify the web interface loads at `http://localhost:3000`.
   - Verify that login and prescription (JSON template loading) work.
   - Verify that PDF download works (resource path resolution).
