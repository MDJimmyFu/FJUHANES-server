from his_client_final import HISClient
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003278373G"
print(f"[*] Fetching history for {target}...")
hist = c.get_anesthesia_history(target)

if hist:
    print(f"[+] Found {len(hist)} billed records.")
    for i, h in enumerate(hist):
        print(f"\n--- Record {i} ---")
        print(f"Date: {h.get('ANEBGNDTTM')}")
        print(f"Method: {h.get('ANENM')}")
        print(f"Procedure: {h.get('ORDPROCED', 'N/A')}")
        print(f"ORDSEQ: {h.get('ORDSEQ')}")
else:
    print("[-] No billed history found.")
