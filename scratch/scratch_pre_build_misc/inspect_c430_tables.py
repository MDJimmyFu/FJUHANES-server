from his_client_final import HISClient
import json, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target_patient = "003189572E"
target_ordseq = "A75177003OR0001" # From previous search
target_date = "20260216"

print(f"[*] Fetching full C430 (Pre-Anesthesia) data for {target_patient} / {target_ordseq}...")
data = c.get_pre_anesthesia_data(target_ordseq, target_patient, opdate=target_date)

if data:
    print(f"[+] Found {len(data)} tables.")
    for table_name, rows in data.items():
        print(f"\n--- Table: {table_name} ({len(rows)} rows) ---")
        if len(rows) > 0:
            # Print unique keys for the table
            print(f"  Keys: {list(rows[0].keys())}")
            # Print sample row if it's likely a report
            if 'RPT' in table_name or 'REPORT' in table_name or 'IMG' in table_name or 'RADIO' in table_name or 'CONTEXT' in str(rows[0]):
                for i, row in enumerate(rows[:3]):
                    print(f"  Row {i}: {row}")
else:
    print("[-] No data found.")
