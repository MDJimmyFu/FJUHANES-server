from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003380272B"

print(f"[*] Testing comprehensive history for {target}...")
history = c.get_comprehensive_patient_history(target)
print(f"[+] Total visits found: {len(history)}")

# Group by type
types = {}
for h in history:
    t = h['type']
    types[t] = types.get(t, 0) + 1

for t, count in types.items():
    print(f"  - {t}: {count} visits")

if history:
    print(f"\n[*] Sample Visit (Recent):")
    v = history[0]
    for k, val in v.items():
        print(f"  {k}: {val}")
    
    print(f"\n[*] Fetching details for case {v['caseno']} ({v['type']})...")
    details = c.get_visit_details(v['caseno'], v['type'])
    print(f"  - Medications: {len(details['meds'])}")
    if details['meds']:
        print(f"    Sample Med: {details['meds'][0]['name']}")
    print(f"  - Consultations: {len(details['consults'])}")
    if details['consults']:
        print(f"    Sample Consult: {details['consults'][0]['dept']} - {details['consults'][0]['reason']}")
else:
    print("[-] No history found for this patient.")
