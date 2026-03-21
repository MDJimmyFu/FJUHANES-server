# Walkthrough: Fixing DM Checkbox PDF Generation Logic

I have corrected the logic that was causing the DM (Diabetes Mellitus) status to be incorrectly reported in the generated PDF. The issue was a keyword mismatch where the code was looking for "Diabetes mellitus", while the HTML used "DM".

## Changes Made

### [SurgerySchedule Component]

#### [legacy_schedule.html](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/templates/legacy_schedule.html)
- Updated the `drawEvalPdfContent` function to use the correct keyword `"DM"` for detail extraction.
- Changed the `isChecked` check to use the explicit element ID `chk_end_dm`, ensuring robust detection even if OAD/Insulin are not selected.

```diff
-            // "Diabetes mellitus" -> DM Note
-            let note = extractSectionDetails("Diabetes mellitus");
+            // "DM" -> DM Note
+            let note = extractSectionDetails("DM");
             if (note && note !== "CHECKED") draw(note, 250.19, 628.75 + 2);
-            checkPhItem("DM", (note && note !== "CHECKED") || isChecked("Diabetes mellitus"));
+            checkPhItem("DM", (note && note !== "CHECKED") || isChecked("chk_end_dm"));
```

#### [index.html](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/templates/index.html)
- Applied a similar fix to the `drawEvalPdfContent` function in the main schedule view for consistency.

```diff
-            // "Diabetes mellitus" -> DM Note
-            let note = extractSectionDetails("Diabetes mellitus");
+            // "DM" -> DM Note
+            let note = extractSectionDetails("DM");
             if (note && note !== "CHECKED") draw(note, 250.19, 628.75 + 2);
-            checkPhItem("DM", (note && note !== "CHECKED") || isChecked("Diabetes mellitus"));
+            checkPhItem("DM", (note && note !== "CHECKED") || isChecked("DM"));
```

## Verification Results

### Logic Verification
- **`extractSectionDetails("DM")`**: Now correctly finds the `span.bold-item` containing "(1) DM (糖尿病)".
- **`isChecked("chk_end_dm")`**: In the legacy schedule, it now directly checks the element with the unique ID `chk_end_dm`.
- **`checkPhItem("DM", ...)`**: When either the main DM checkbox is checked or notes are present, the "DM Yes" checkbox in the PDF is now correctly ticked.

The fixes ensure that if a patient has the primary "DM" checkbox checked, the PDF will reflect "DM YES" regardless of the sub-options (OAD/Insulin).
