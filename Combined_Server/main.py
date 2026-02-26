import multiprocessing
import os
import sys
import time
import webbrowser

# Ensure the root directory is in sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

def run_surgery():
    # Adding subdirectory to path to handle internal imports of the sub-app
    # such as 'import his_client_final'
    sys.path.insert(0, os.path.join(base_dir, 'SurgerySchedule'))
    from SurgerySchedule.app import app as surgery_app
    print("[*] Surgery Schedule Server starting on port 5000...")
    surgery_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def run_prescribe():
    # Same for AutoPrescribe
    sys.path.insert(0, os.path.join(base_dir, 'AutoPrescribe'))
    from AutoPrescribe.app import app as prescribe_app
    print("[*] AutoPrescribe Server starting on port 3000...")
    prescribe_app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)

def open_browser():
    time.sleep(5)
    print("[*] Opening browser...")
    try:
        webbrowser.open("http://127.0.0.1:5000")
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:3000")
    except Exception as e:
        print(f"[-] Browser error: {e}")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    print("[*] Starting Combined Servers (SurgerySchedule & AutoPrescribe)...")
    
    p1 = multiprocessing.Process(target=run_surgery)
    p2 = multiprocessing.Process(target=run_prescribe)
    
    p1.start()
    p2.start()
    
    # Run browser opener in a separate thread
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        p1.join()
        p2.join()
    except KeyboardInterrupt:
        print("\n[*] Stopping servers...")
        p1.terminate()
        p2.terminate()
        p1.join()
        p2.join()
        print("[*] Servers stopped.")
