# Surgery Board Feature Walkthrough

The Surgery Board is a new, dedicated view designed to provide a real-time, comprehensive overview of the surgical schedule across all 18 operating rooms.

## Core Features

### 1. Header Information
-   **Real-time Clock**: A prominent, lively clock displaying the exact current time (down to the second) sits at the top right of the screen.
-   **Last Update**: The exact time of the last successful data pull from the HIS server is displayed directly beneath the real-time clock.

### 2. 18-Room Horizontal Scroll Layout
-   **Structure**: The UI features 18 distinct horizontal lanes, one for each operating room (OR 01 to OR 18).
-   **Navigation**: Each lane allows for smooth horizontal scrolling, enabling staff to view an unlimited number of scheduled surgeries in a single room without breaking the page layout.
-   **Clean View**: Surgeries marked as "完成" (Completed) are automatically filtered out of the board to keep focus on pending and active cases.

### 2. Surgery Cards
Each surgery is represented by a cleanly designed card containing key information:
-   **Status Badge (Top Left)**: Clearly indicates the current phase (手術中, 等候區, 叫刀). Colors are tied to the status for quick visual scanning. 
    -   *Additionally, on the standard/legacy Surgery Schedule views (`index.html`), a green checkmark `✓` will appear next to this status if the anesthesia assessment is complete.*
-  **Anesthesia Method & Assessment Status (Top Right)**: Displays the required anesthesia (e.g., GE, SA). Crucially, **if the patient's pre-anesthesia assessment is complete, the background of this badge turns distinctively green**, allowing for rapid identification. Hovering over it also provides a tooltip confirming the status.
-  **Procedure & Patient Info (Center)**: 
    -   **Procedure Name**: The name of the operation. **Long names automatically scroll** for full visibility.
    -   **Patient Identification**: Displays the **Patient Name** and **Ward/Bed Number**.
    -   **Consolidated Info**: The **Chart Number** and **Surgeon Name** are displayed together on a single line to maximize vertical screen space.
-  **Estimated Duration & Emergency Indicator (Bottom)**: Displays the planned length of the surgery in minutes (`OROPMIN`). If the surgery is an emergency, a distinct color-coded badge (Red for **A**, Orange for **B**, Green for **C**) indicates the emergency severity level at the bottom right.

### 3. Intelligent Sorting Algorithm & Cross-Midnight Logic
Within each operating room lane, uncompleted surgeries are sorted dynamically. **The board autonomously pulls data from both yesterday and today**, guaranteeing that prolonged, cross-midnight surgeries are never orphaned.
The primary status prioritization is:
1.  **手術中** (In Surgery)
2.  **等候區** (Waiting Area)
3.  **叫刀** (Called)
4.  **Date Prioritization**: If multiple surgeries share the same status (or are entirely unstarted), earlier operation dates automatically float to the top.
5.  **Console Order**: Finally, falling back to the standard HIS console sequencing logic (`OROPROOMSEQ_OPSTA_NUM` followed by `OROPROOMSEQ_DR_NUM`).

### 4. Customizable Settings (Bottom Right Gear Icon)
A fully functional settings modal allows users to tailor the board to their environment. Settings are saved locally to the browser (`localStorage`), meaning preferences persist across page reloads.

-   **Theme Toggle**: Users can switch between a Light Mode, a high-contrast Dark Mode, or choose "Auto" to match their operating system preferences.
-   **Hide Empty Rooms**: A toggle that dynamically removes lanes for operating rooms that have no active surgeries scheduled, maximizing screen real estate.
-   **Hide Local Surgeries (LA/NI)**: A default-enabled toggle that hides minor surgeries where the anesthesia method is Local Anesthesia (`LA`) or No Intervention (`NI`), focusing the board on major operations.
-   **Auto-Refresh Timer**: An adjustable input allowing users to set how frequently the board pulls fresh data from the server (default is 5 minutes).

## Advanced Search Functionality (Standard Views)
When utilizing the standard list views (`index.html` or `legacy_schedule.html`), the backend routing logic has been vastly improved to directly forward range-matched date parameters to the HIS C250 facade via binary patching. This means users are no longer limited to searching a single day and can query large blocks of cross-temporal operations seamlessly.

## Verification Results
- [x] Backend `/board` route successfully serves the new template.
- [x] Data fetch successfully retrieves today's surgery list via the existing C250 API interface.
- [x] Horizontal scroll layout renders 18 rooms correctly.
- [x] Sorting algorithm accurately groups and prioritizes cards by status.
- [x] Settings modal successfully toggles Dark Mode, hides empty lanes dynamically, and adjusts the refresh timer.
