from his_client_final import HISClient
import json, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target_patient = "003363078D"
target_ordseq = "A75176750OR0001" # From previous search
target_date = "20260211"

print(f"[*] Fetching C430 tables for patient {target_patient}...")
data = c.get_pre_anesthesia_data(target_ordseq, target_patient, opdate=target_date)

if data:
    print(f"[+] Total Tables: {len(data)}")
    print(f"[*] Table Names: {list(data.keys())}")
    
    for tn in ['CXR', 'EKG', 'RADIO_IMG_RPT', 'REPORT', 'RADIO']:
        if tn in data:
            print(f"\n--- Found Table: {tn} ({len(data[tn])} rows) ---")
            for i, row in enumerate(data[tn][:3]):
                print(f"  Row {i}: {row}")
else:
    print("[-] No data found.")
