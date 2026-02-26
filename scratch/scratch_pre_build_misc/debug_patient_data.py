from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003600459I"

print(f"[*] Analyzing history for {target}...")
history = c.get_comprehensive_patient_history(target)

for h in history:
    print(f"[{h['date']}] {h['type']} - Dept: {h['dept']} - Doctor: {h['doctor']} - Case: {h['caseno']}")
    print(f"    Diagnosis: {h['diagnosis']} ({h['diagnosis_desc']})")
    
    # Check details for each visit
    details = c.get_visit_details(h['caseno'], h['type'])
    if details['consults']:
        print(f"    [!] Consultations found:")
        for cons in details['consults']:
            print(f"        - [{cons['date']}] {cons['dept']} ({cons['doctor']}): {cons['reason']} (Status: {cons['status']})")
    print("-" * 20)
