from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
hhis = "003457263J"

print(f"[*] Fetching Anesthesia History for {hhis}...")
hist = c.get_anesthesia_history(hhis)

print(f"[+] Found {len(hist)} records.")

for i, h in enumerate(hist):
    print(f"\n--- Record {i+1} ---")
    print(json.dumps(h, indent=2, ensure_ascii=False))
