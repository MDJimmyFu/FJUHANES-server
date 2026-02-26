import os
import subprocess
import sys

def build():
    # Install pyinstaller if not present
    try:
        import PyInstaller
    except ImportError:
        print("[*] Installing pyinstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Path separator for --add-data (Windows uses ; while Mac/Linux uses :)
    sep = os.pathsep

    # Define the command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--console",
        "--name", "SurgerySchedule",
        "--add-data", f"templates{sep}templates",
        "--add-data", f"static{sep}static",
        "--add-data", f"c250_payload_1.bin{sep}.",
        "--add-data", f"c430_payload_0.bin{sep}.",
        "--add-data", f"q050_payload_0.bin{sep}.",
        "--add-data", f"c250_activate.bin{sep}.",
        "--add-data", f"HISExmFacade_payload_0.bin{sep}.",
        "app.py"
    ]

    print(f"[*] Executing: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    print("\n[SUCCESS] Build complete. Check the 'dist' folder.")

if __name__ == "__main__":
    build()
