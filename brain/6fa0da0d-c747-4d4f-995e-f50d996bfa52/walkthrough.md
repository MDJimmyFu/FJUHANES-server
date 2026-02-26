# Walkthrough: Combined Server Executable

I have successfully combined `SurgerySchedule` and `AutoPrescribe` into a single standalone executable. This allows you to run both servers simultaneously from one file while preserving their separate functions and ports.

## Key Changes

### 1. Unified Structure
A new `Combined_Server` directory was created, containing both applications in specialized subdirectories:
- `SurgerySchedule/`: Port 5000 (Surgery List & Details)
- `AutoPrescribe/`: Port 3000 (PCA, PCEA, Painless labor & Intubation prescriptions) **[Updated to Version 2]**

### 2. Main Entry Point (`main.py`)
A robust entry script was created to:
- Use `multiprocessing` to run both Flask applications in isolation.
- Automatically launch your browser to both server addresses:
  - `http://localhost:5000`
  - `http://localhost:3000`

### 3. Standalone Executable
A single file `Combined_Server.exe` has been generated in `Combined_Server/dist/`. This file contains all code, templates, static assets, and pre-anesthesia data binary files. I have also fixed the path resolution logic to ensure templates and static files are found correctly in both development and the final executable.

## How to Use

1. Navigate to [Combined_Server/dist](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/dist).
2. Run `Combined_Server.exe`.
3. The console will show both servers starting, and your default browser should open tabs for both applications.

## Location of Files

- **Source Code**: [Combined_Server/](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/)
- **Executable**: [Combined_Server/dist/Combined_Server.exe](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/dist/Combined_Server.exe)
- **Build Script**: [Combined_Server/build_combined.py](file:///c:/Users/A03772/.gemini/antigravity/Combined_Server/build_combined.py)

> [!NOTE]
> The source directories `scratch` and `AutoPrescribe_Portable` remain untouched as requested.
