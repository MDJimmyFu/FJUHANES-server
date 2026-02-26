# Network Analysis and API Client Implementation Plan

## Goal
Analyze network traffic from the target HIS application to reverse-engineer the API endpoints and authentication mechanism, then update `his_api_client.py` to function correctly.

## User Review Required
- **Capture Strategy**: Protocol is likely HTTPS.
- **Recommended Tool**: **Fiddler Classic** (easiest for HTTPS decryption) or **Wireshark** (requires key log).
- **User Action**: Install Fiddler, enable HTTPS decryption, capture login, export to **HAR** or **SAZ**.

## Proposed Changes

### Analysis Phase
1.  **Identify Endpoint**:
    -   Use `netstat -nb` to find the application's connection (IP:Port).
    -   Determine if it's HTTP or HTTPS.
2.  **Capture Traffic**:
    -   User installs/runs Fiddler.
    -   Capture traffic during `login` and `patient search`.
3.  **Analyze Data**:
    -   Import HAR file (text) or analyze user-provided screenshots/logs.

### Implementation Phase (`his_api_client.py`)
1.  Update `login()` method with:
    -   Correct `login_url`.
    -   Correct payload keys (e.g., `user` vs `username`, `pwd` vs `password`).
    -   Token extraction logic if necessary.
2.  Update `get_patient_data()` method with:
    -   Correct `endpoint`.
    -   Correct query parameters or JSON body.

## Verification Plan
### Automated Tests
-   Run `his_api_client.py` (updated) and verify it prints "Login successful!".

### Manual Verification
-   Compare script output with actual browser behavior.
