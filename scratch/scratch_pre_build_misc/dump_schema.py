from his_client_final import HISClient
import sys
import collections

def analyze_schema():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    client = HISClient()
    print("[*] Gathering data for schema analysis...")
    
    # 1. C250
    surgeries = client.get_surgery_list()
    if not surgeries:
        print("[-] C250 failed.")
        return

    print("\n=== C250: Surgery List ===")
    print(f"Key Candidates: ORDSEQ, HHISTNUM")
    print("Fields:")
    for k in surgeries[0].keys():
        print(f"  - {k}")

    target = surgeries[0]
    
    # 2. C430
    c430_data = client.get_pre_anesthesia_data(target['ordseq'], target['hhistnum'])
    print("\n=== C430: Pre-Anesthesia ===")
    if c430_data:
        for table, rows in c430_data.items():
            print(f"\nTable: {table}")
            if rows:
                keys = rows[0].keys()
                # Guess ID: look for 'NO', 'ID', 'SEQ', 'KEY'
                candidates = [k for k in keys if any(x in k for x in ['NO', 'ID', 'SEQ', 'KEY', 'REC'])]
                print(f"  Potential Keys: {', '.join(candidates)}")
                print("  Fields:")
                for k in keys:
                     print(f"    - {k} (e.g. {rows[0][k]})")
    
    # 3. Q050
    q050_data = client.get_anesthesia_charging_data(target['ordseq'], target['hhistnum'])
    print("\n=== Q050: Anesthesia Charging ===")
    if q050_data:
        for table, rows in q050_data.items():
            print(f"\nTable: {table}")
            if rows:
                keys = rows[0].keys()
                candidates = [k for k in keys if any(x in k for x in ['NO', 'ID', 'SEQ', 'KEY', 'REC'])]
                print(f"  Potential Keys: {', '.join(candidates)}")
                print("  Fields:")
                for k in keys:
                     print(f"    - {k} (e.g. {rows[0][k]})")

if __name__ == "__main__":
    analyze_schema()
