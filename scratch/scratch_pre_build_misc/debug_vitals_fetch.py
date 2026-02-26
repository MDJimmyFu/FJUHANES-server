from his_client_final import HISClient
import json

c = HISClient()
# ORDSEQ: A75176986OR0041, HHISNUM: 003617083J
print(f"[*] Debugging Vitals Fetching...")

# 1. Fetch Surgery List to find a valid ORDSEQ
surgeries = c.get_surgery_list()
if not surgeries:
    print("[-] No surgeries found. Exiting.")
    exit()

target = surgeries[0]
print(f"[*] Target Patient: {target['HNAMEC']}")
print(f"[*] ORDSEQ: {target['ORDSEQ']}")
print(f"[*] HHISTNUM: {target['HHISTNUM']}")

# 2. Get Raw Vitals from EXM
vitals = c.get_vitals_from_exm(target['HHISTNUM'], target['ORDSEQ'])

print("\n--- Parsed Vitals ---")
print(json.dumps(vitals, indent=4, ensure_ascii=False))

print("\n--- Raw SQL Response Dump (Simulated) ---")
# I'll modify the client momentarily to print raw if needed, but first check parsed.
