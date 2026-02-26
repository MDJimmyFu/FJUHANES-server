# implementation_plan.md - Adding Settings Menu and Theme Support

This plan details the addition of a floating settings menu to the surgery schedule page, enabling auto-refresh and theme customization.

## Proposed Changes

### [Component] Dynamic Data & Reports Refinement

#### [MODIFY] [legacy_schedule.html](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/SurgerySchedule/templates/legacy_schedule.html)

- **Vitals & Lab Rendering**:
    - Replace hardcoded `background:#f8f9fa` and `background:white` in JS rendering with CSS classes or variables.
    - Ensure field labels use `var(--text-muted)` and values use `var(--primary)`.

- **Lab & Imaging Reports**:
    - Refactor report link styles (68 imaging, 64 sampling) to use theme-compatible colors.
    - Add `.theme-dark` specific overrides for these colored boxes (Imaging, Sampling, EKG) to ensure high readability.
    - Use `rgba` or theme-aware variables for backgrounds.

- **Tables & Lists**:
    - Update `toggleAneDetail` and `toggleVisitDetail` background colors to use `var(--header-bg)`.
    - Ensure all nested tables follow the global theme table styles.

## Verification Plan

### Automated Tests
- N/A

### Manual Verification
1.  **Physiological Data**: Verify the grid of vitals (Height, Weight, etc.) is fully themed.
2.  **Lab Data**: Verify the lab values grid is fully themed.
3.  **Reports**: Click "Imaging Reports" and "Lab Reports" to verify their link boxes are readable and themed.
4.  **History Tables**: Expand anesthesia and patient history to verify the expanded rows are themed (not hardcoded white).
