from his_client_final import HISClient
import sys

def debug_missing_codes(target_caseno):
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    client = HISClient()
    print(f"[*] Searching for Case No: {target_caseno}...")
    
    surgeries = client.get_surgery_list("20260211")
    found = next((s for s in surgeries if target_caseno in s['ordseq']), None)
    
    if found:
        print(f"[+] Found Patient: {found['patient']} (ORDSEQ: {found['ordseq']})")
        
        charging = client.get_anesthesia_charging_data(found['ordseq'], found['hhistnum'])
        
        missing_codes = ["55107082", "55107081", "55107030", "55106140", "551N0100", "551N0110", "551N0060", "551N0310"]
        found_codes = []
        
        if charging:
             # Check every possible table
             for table, records in charging.items():
                 for r in records:
                     # Check all values in the record
                     for k, v in r.items():
                         if str(v) in missing_codes:
                             print(f"[!] Found {v} in Table {table} (Field: {k})")
                             print(f"    Record: {r}")
                             found_codes.append(str(v))
                             
             print(f"\nSummary:")
             print(f"Found: {len(set(found_codes))}")
             print(f"Missing: {len(missing_codes) - len(set(found_codes))}")
             
             # Also print Anesthesia Supervision Name
             if 'ORRANER' in charging and charging['ORRANER']:
                 print(f"\nAnesthesiologist (ANEDOCNMC): {charging['ORRANER'][0].get('ANEDOCNMC')}")
                 print(f"Supervisor (ANESUPVNMC): {charging['ORRANER'][0].get('ANESUPVNMC')}")

        else:
             print("[-] No charging data found.")
    else:
        print("[-] Case not found.")

if __name__ == "__main__":
    debug_missing_codes("75176750")
