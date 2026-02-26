from his_client_final import HISClient
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003380272B"
print(f"[*] Fetching admission history for {target}...")
hist = c.get_admission_history(target)

if hist:
    print(f"[+] Found {len(hist)} records.")
    for i, h in enumerate(hist[:5]):
        print(f"\n--- Admission {i} ---")
        print(f"Date: {h.get('admdt')}")
        print(f"Dept: {h.get('dept')}")
        print(f"Diagnosis: {h.get('diagnosis')}")
        print(f"Doctor: {h.get('doctor')}")
else:
    print("[-] No admission history found.")
