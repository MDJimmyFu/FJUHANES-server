from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807040"

print(f"[*] Verifying fixed client for Case {caseno}...")
details = c.get_visit_details(caseno, 'EMG')

if details['emg_notes']:
    en = details['emg_notes']
    
    print("\n--- ADM NOTE ---")
    adm = en.get('adm_note', {})
    print(f"HEENT length: {len(adm.get('HEENT', ''))}")
    print(f"HEENT start: {adm.get('HEENT', '')[:50]}...")
    print(f"PI length: {len(adm.get('PRESENT_ILLNESS', ''))}")
    
    print("\n--- POMR ---")
    pns = en.get('progress_notes', [])
    print(f"Found {len(pns)} notes.")
    for i, pn in enumerate(pns):
        print(f"Note {i+1}:")
        print(f"  S length: {len(pn.get('S', ''))}")
        print(f"  A length: {len(pn.get('A', ''))}")
        print(f"  A content start: {pn.get('A', '')[:50]}...")
else:
    print("[-] No EMG notes returned.")
