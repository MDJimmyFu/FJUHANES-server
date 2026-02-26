# Imaging Report Integration Plan

The goal is to incorporate imaging reports from the `ORMC430` endpoint into the patient details view, ensuring that all available imaging data (besides EKG Link) is displayed correctly.

## Proposed Changes

### [app.py](file:///c:/Users/A03772/.gemini/antigravity/scratch/app.py)
- Update `patient_detail` and legacy endpoints to consolidate imaging-related tables from `ORMC430`.
- Specifically, merge tables like `CXR`, `INSPECTION_CXR`, and `RADIO_IMG_RPT` if they exist into a single list for the frontend.
- Standardize the name to `cxr` (as expected by some parts) or ensure mapping is clear.

### [templates/legacy_schedule.html](file:///c:/Users/A03772/.gemini/antigravity/scratch/templates/legacy_schedule.html)
- Update `showDetail` to look for the correct consolidated imaging key (e.g., `CXR`).
- Enhance the imaging report display to handle missing `CXRURL` by showing the report information (e.g., `ORDPROCED`) clearly even without a link.
- If `ORDAPNO` is present, look for a way to link to the report or just display the ID.

### [his_client_final.py](file:///c:/Users/A03772/.gemini/antigravity/scratch/his_client_final.py)
- Ensure `-parse_dataset` correctly captures all potential imaging tables.
- Investigate if other report types (CT, MRI) use different table names and ensure they are extracted.

## Verification Plan

### Manual Verification
- Check patients with known imaging results (e.g., `003574100F` who has an ECHO in the `CXR` table).
- Verify that the "Imaging Reports" section in the UI displays these items correctly.
- Ensure the EKG Link remains functional.
