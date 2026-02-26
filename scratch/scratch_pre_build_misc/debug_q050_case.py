from his_client_final import HISClient
import sys

def debug_case(target_caseno):
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    client = HISClient()
    print(f"[*] Searching for Case No: {target_caseno}...")
    
    # We know it's in yesterday's list from previous interaction
    surgeries = client.get_surgery_list("20260211")
    
    found = None
    if surgeries:
        for s in surgeries:
            if target_caseno in s['ordseq']:
                found = s
                break
    
    if found:
        print(f"[+] Found Patient: {found['patient']} (ORDSEQ: {found['ordseq']})")
        
        print("\n[*] Fetching Full Q050 Data...")
        charging = client.get_anesthesia_charging_data(found['ordseq'], found['hhistnum'])
        
        if charging:
             for table, records in charging.items():
                 print(f"\n=== TABLE: {table} ({len(records)} records) ===")
                 for i, r in enumerate(records):
                     print(f"\n  -- Record {i} --")
                     for k, v in r.items():
                         print(f"  {k}: {v}")
        else:
             print("[-] No charging data found.")

    else:
        print("[-] Case not found.")

if __name__ == "__main__":
    debug_case("75176750")
