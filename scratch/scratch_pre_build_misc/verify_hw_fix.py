from his_client_final import HISClient
import json, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target_patient = "003189572E"

print(f"[*] Verifying vitals fix for patient {target_patient}...")
vitals = c.get_vitals_from_exm(target_patient)

print("\nResulting Vitals (Mapped):")
print(json.dumps(vitals, indent=2))

if vitals.get('HEIGHT') == '174' and vitals.get('WEIGHT') == '90':
    print("\n[SUCCESS] Height/Weight correctly retrieved from VITALSIGNUPLOAD fallback.")
else:
    print("\n[FAILURE] Height/Weight not as expected.")
