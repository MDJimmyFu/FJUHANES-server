# Scanner Page Implementation Plan

Establish a new webpage designed for mobile use that allows users to select a patient currently in surgery and display their Medical Record Number (MRN) and the staff member's ID as barcodes for easy scanning.

## Proposed Changes

### SurgerySchedule Server

#### [MODIFY] [app.py](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/app.py)
- Add a new route `@app.route('/scanner')` that renders the `scanner.html` template.
- This route will be protected by `@login_required`.

#### [NEW] [scanner.html](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/templates/scanner.html)
- **UI Design**: A clean, mobile-first interface.
- **Patient List**: Fetches today's surgery list from `/api/surgery_list` and filters for patients with `STATUS === '手術中'`.
- **Barcode Display**:
    - When a patient is selected, show their MRN and the current User's ID (from session).
    - Use `JsBarcode` (CDN) for 1D barcodes (Code 128).
    - Use `QRCode.js` (CDN) for 2D barcodes.
    - Add a toggle button to switch between 1D and 2D modes.
- **Scanning Optimizations**:
    - Full-screen mode request (where supported).
    - Set background to pure white and maximize contrast.
    - Implement a "Keep Screen On" feature using the Screen Wake Lock API if available.
    - Visual hint for the user to manually increase brightness if the automated method is restricted by the browser.

## Verification Plan

### Manual Verification
1. Log in to the application.
2. Navigate to `http://localhost:5000/scanner`.
3. Verify that the list shows patients currently in surgery.
4. Click on a patient and verify that two barcodes appear (MRN and Staff ID).
5. Test the 1D/2D toggle.
6. Verify the UI looks good on small (mobile) screen sizes using browser dev tools.
7. Confirm that clicking the "Scanner optimization" button attempts to keep the screen on.
