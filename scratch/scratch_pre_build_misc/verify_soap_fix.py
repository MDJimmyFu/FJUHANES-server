from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807040"

print(f"[*] Verifying fix for Case {caseno}...")
details = c.get_visit_details(caseno, 'EMG')

if details['emg_notes'] and details['emg_notes']['progress_notes']:
    for pn in details['emg_notes']['progress_notes']:
        print(f"    Note from {pn.get('OPNM')}:")
        print(f"      S: '{pn.get('S')}' (Type: {type(pn.get('S'))})")
        print(f"      O: '{pn.get('O')}'")
        print(f"      A: '{pn.get('A')}'")
        print(f"      P: '{pn.get('P')}'")
        
        # Check if keys exist
        for k in ['S', 'O', 'A', 'P']:
             if k not in pn:
                 print(f"    [!] Error: Key {k} missing!")
else:
    print("[-] No progress notes found. This case might truly have none despite user report, or I'm missing a table.")
