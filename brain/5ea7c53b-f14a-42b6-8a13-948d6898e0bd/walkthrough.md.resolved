# Scanner Page Walkthrough

I have added a new scanner-friendly page to the `SurgerySchedule` application. This page allows clinicians to select a patient currently in surgery and display their Medical Record Number (MRN) and the logged-in user's Staff ID as barcodes (1D or 2D).

## Changes Made

### Backend
- **[app.py](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/app.py)**: Added a new route `@app.route('/scanner')` which renders the scanner interface.

### Frontend
- **[scanner.html](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/templates/scanner.html)**:
    - **Mobile-First Design**: A clean, high-contrast interface optimized for handheld use.
    - **2-Column Layout**: Both the **Patient List** and the **Barcodes** are displayed in a 2-column grid to maximize space on larger screens (tablets/desktops).
    - **Responsive Design**: On mobile devices, the layout automatically adjusts to a single column for better readability.
    - **Dynamic Patient List**: Automatically fetches the surgery list and filters for patients with the status "手術中" (In Surgery).
    - **Barcode Support**:
        - **1D Barcode**: Uses `JsBarcode` (Code 128) for standard scanners.
        - **2D Barcode**: Uses `QRCode.js` for camera-based scanning.
        - Includes a toggle button to switch between modes.
    - **Scanning Optimization**:
        - Includes a button to request Full-Screen mode.
        - Uses the **Screen Wake Lock API** to keep the display active while a barcode is being shown.

## How to Use
1. Access the application on a mobile device and log in.
2. Navigate to `/scanner` (e.g., `http://[server-ip]:5000/scanner`).
3. Select a patient from the list.
4. The barcodes for the Patient MRN and Staff ID will be displayed.
5. Use the "Toggle" button if you need to switch between 1D and 2D formats.
6. Use the lightbulb icon (💡) to request full screen for better scanability.

## Release Details
- **Git Commit**: `feat: add mobile scanner page with 2-column layout`
- **Build**: Successfully rebuilt `Combined_Server.exe` in the `dist` folder.
- **Verification**: Verified the backend route and layout structure.
