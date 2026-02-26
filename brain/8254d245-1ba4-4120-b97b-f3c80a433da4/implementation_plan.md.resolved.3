# Data Access Workflow Design

## Goal Description
Design a technical process to retrieve data programmatically or directly from the source, bypassing the standard HIS (Hospital Information System) user interface. This is typically done for analytics, interoperability, or custom application integration.

## User Review Required
> [!IMPORTANT]
> **Security & Compliance**: Accessing medical data outside the standard HIS UI requires strict adherence to data privacy regulations (e.g., GDPR, HIPAA, local laws). Ensure you have authorized administrative or developer access to the underlying systems.

- **Data Source**: What specific database (SQL Server, Oracle, MySQL) or interface (HL7, FHIR) is available?
- **Authentication**: How will the external process authenticate?
- **Read/Write**: Is this purely for reading data, or is write-back required?

## Proposed Workflows

## Proposed Workflows

### The "API Replay" Strategy (Best Practice)
You mentioned the HIS uses web protocols. This is the **Gold Standard** for automation. Instead of simulating a mouse (which is slow and buggy), we will simulate the *network requests* directly.

#### 1. The Concept
Even a Desktop App often talks to a server using HTTP/HTTPS, just like a browser.
-   **User Action**: You click "Search Patient" in the App.
-   **Real Action**: The App sends a `POST /api/search_patient` request to the server.
-   **Our Goal**: Write a Python script that sends that exact same `POST` request.

#### 2. How we get there (The "Sniffing" Phase)
We need to see what the App is saying to the Server.
-   **For Web Parts**: Use Chrome Developer Tools (F12) -> Network Tab.
-   **For Desktop Parts**: Use a traffic inspector tool like **Fiddler Classic** or **Wireshark**.
    -   *Action*: You run Fiddler, then perform the action in the HIS. Fiddler will show us the URL, Headers, and Cookies.

#### 3. The "Orchestrator" (Python Script)
Once we know the "Secret Handshake" (URL + Headers):
-   We use the Python `requests` library to fetch data instantly.
-   No mouse movement needed. It runs in the background.
-   **Speed**: Milliseconds instead of seconds.

## Patient Assessment Tool Design
-   **Tech Stack**: Python + Streamlit.
-   **Data Flow**:
    1.  Python Script logs in (using your credentials).
    2.  Fetches JSON/XML data for the patient.
    3.  Streamlit Dashboard calculates scores and displays the assessment view.

## Next Steps
1.  **Tool Check**: Can you install **Fiddler Classic** (free) on this computer?
2.  **Capture**: I will guide you to capture one request (e.g., "Get Patient Info").
3.  **Replay**: I will write a Python script to mimic that request.
