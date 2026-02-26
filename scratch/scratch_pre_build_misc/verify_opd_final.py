from his_client_final import HISClient
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46402990"

print(f"[*] Verifying OPD notes for {caseno}...")
try:
    details = c.get_visit_details(caseno, 'OPD')
    if details['opd_notes']:
        on = details['opd_notes']
        print("[+] OPD Notes Found:")
        print(f"  S: {on['S']}")
        print(f"  O: {on['O']}")
        print(f"  A: {on['A']}")
        print(f"  P: {on['P']}")
    else:
        print("[-] No OPD notes found.")
except Exception as e:
    print(f"[-] Error: {e}")
