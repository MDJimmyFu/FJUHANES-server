from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807673"

print(f"[*] Simulating full details fetch for {caseno}...")
details = c.get_visit_details(caseno, 'EMG')

print("\n--- EMG CLINICAL NOTES ---")
if details['emg_notes']:
    en = details['emg_notes']
    print("[1] Triage / Chief Complaint:")
    print(f"    CC: {en['triage'].get('CHIEF_COMPLAINT')}")
    
    print("\n[2] Admission Note:")
    print(f"    CC: {en['adm_note'].get('CHIEF_COMPLAINTS')}")
    print(f"    PI: {en['adm_note'].get('PRESENT_ILLNESS')}")
    print(f"    PE HEENT: {en['adm_note'].get('HEENT')}")
    
    print("\n[3] Progress Notes (SOAP):")
    for pn in en['progress_notes']:
        print(f"    - [{pn['OPNM']}] S: {pn['S']} O: {pn['O']}")
else:
    print("[-] No EMG notes found.")
