# Add Patient Info to Surgery Cards

Add patient name, chart number (medical record number), and ward/bed number to the surgery cards displayed on the Surgery Board (`board.html`).

## Proposed Changes

### Surgery Board Component

#### [MODIFY] [board.html](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/templates/board.html)
- Update `createCardHTML(s)` to extract `HNAMEC`, `HHISTNUM`, and `HBED`.
- Add a new section in the card body to display this information.
- Adjust CSS styles to accommodate the additional text while maintaining a clean UI.

## Verification Plan

### Manual Verification
- Open the Surgery Board and verify that each card now displays:
    - Patient Name (HNAMEC)
    - Chart Number (HHISTNUM)
    - Ward/Bed Number (HBED)
- Ensure the layout remains responsive and aesthetically pleasing (no text overflow or overlapping).
- Verify the executable rebuilds successfully.
