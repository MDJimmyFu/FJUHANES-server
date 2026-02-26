from his_client_final import HISClient
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
# Patient with known history
target = "003086248H" 
print(f"[*] Fetching history for {target}...")
hist = c.get_anesthesia_history(target)

if hist:
    print(f"[+] Found {len(hist)} records.")
    print("Columns in first record:")
    for k, v in hist[0].items():
        print(f"{k}: {v}")
else:
    print("[-] No history found.")
