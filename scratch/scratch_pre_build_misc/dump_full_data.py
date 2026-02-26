from his_client_final import HISClient
import sys

def dump_all():
    # Ensure stdout handles UTF-8 on Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    client = HISClient()
    
    # 1. Get List
    print("[*] Fetching surgery list...")
    surgeries = client.get_surgery_list()
    
    if not surgeries:
        print("[-] No surgeries found.")
        return

    # 2. Pick first patient
    target = surgeries[0]
    print(f"[*] Target Patient: {target['patient']} (ORDSEQ: {target['ordseq']})")
    
    # 3. Fetch Detail
    print("[*] Fetching full pre-anesthesia data...")
    details = client.get_pre_anesthesia_data(target['ordseq'], target['hhistnum'])
    
    if details:
        print(f"\n[+] Successfully extracted {len(details)} data tables.")
        
        for table_name, records in details.items():
            print(f"\n{'='*20} TABLE: {table_name} ({len(records)} records) {'='*20}")
            
            for i, record in enumerate(records):
                print(f"\n  --- Record {i+1} ---")
                for key, value in record.items():
                    print(f"  {key:<20}: {value}")
    else:
        print("[-] No details found.")

if __name__ == "__main__":
    dump_all()
