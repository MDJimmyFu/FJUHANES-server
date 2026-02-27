# Fixing DM Checkbox PDF Generation Logic

The goal is to ensure that when a patient is checked for "DM" (Diabetes Mellitus) but not for "OAD" or "Insulin," the generated PDF correctly reflects "DM YES." Currently, the code uses "Diabetes mellitus" as a keyword to find the DM status, but this keyword does not exist in the HTML labels, causing the logic to fail.

## Proposed Changes

### [SurgerySchedule Component]

#### [MODIFY] [legacy_schedule.html](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/templates/legacy_schedule.html)

Update the `drawEvalPdfContent` function to use correctly matching keywords/IDs for DM.

- Change keyword from "Diabetes mellitus" to "DM" for `extractSectionDetails`.
- Change `isChecked` call to use the specific ID `chk_end_dm`.

#### [MODIFY] [index.html](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/templates/index.html)

Update the `drawEvalPdfContent` function for consistency (though it appears to be a different version of the form).

- Change keyword from "Diabetes mellitus" to "DM" for both `extractSectionDetails` and `isChecked`.

---

## Verification Plan

### Manual Verification
1. Open the Surgery Schedule page (legacy version).
2. Select a patient and open the "Anesthesia Evaluation Form" (麻醉評估單).
3. Check only the "(1) DM (糖尿病)" checkbox in the Endocrine System section. Leave "OAD" and "Insulin" unchecked.
4. Click "產生麻醉評估單 (PDF)".
5. Open the generated PDF and verify that "DM Yes" is checked.
6. Repeat the test with "(1) DM (糖尿病)" AND "OAD" checked, and verify "DM Yes" is still checked.
7. Repeat the test with nothing checked in the DM section, and verify "DM No" is checked in the PDF.
