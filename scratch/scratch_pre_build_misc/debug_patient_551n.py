from his_client_final import HISClient
import json, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target_patient = "003189572E"
target_date = "20260216"

print(f"[*] Searching for patient {target_patient} on {target_date}...")
surgeries = c.get_surgery_list(target_date)

found = None
if surgeries:
    for s in surgeries:
        if s.get('HHISTNUM') == target_patient:
            found = s
            break

if found:
    print(f"[+] Found patient: {found.get('patient', 'Unknown')}")
    print(f"    ORDSEQ: {found.get('ORDSEQ')}")
    print(f"    HHISTNUM: {found.get('HHISTNUM')}")
    
    ordseq = found.get('ORDSEQ')
    hhistnum = found.get('HHISTNUM')
    
    print(f"\n[*] Fetching Q050 (Charging) data for {ordseq}...")
    charging = c.get_anesthesia_charging_data(ordseq, hhistnum)
    
    if charging:
        print(f"[+] Retrieved {len(charging)} tables.")
        for table, rows in charging.items():
            print(f"\n--- Table: {table} ({len(rows)} rows) ---")
            # If it's a known table with relevant codes, list them
            if table in ['OPDORDM', 'COMMON_ORDER', 'ANEORDER', 'OCCURENCS']:
                for row in rows:
                    pcode = row.get('PFKEY') or row.get('PFCODE') or row.get('ORDPROCED')
                    pname = row.get('PFNM') or row.get('ORDPROCED')
                    if pcode and ('551N' in pcode or '551' in pcode):
                        print(f"  MATCH: {pcode} | {pname}")
                    # Also print first few rows just in case
                if len(rows) > 0 and table == 'OPDORDM':
                    print(f"  (First row sample: {rows[0]})")
    else:
        print("[-] No charging data found.")
else:
    print(f"[-] Patient {target_patient} not found on {target_date} in surgery list.")
    
    # Try searching PAT_ADM_CASE via SQL as a backup
    print("\n[*] Searching via SQL backup (PAT_ADM_CASE)...")
    history = c.get_anesthesia_history(target_patient)
    if history:
        print(f"[+] Found {len(history)} historical records.")
        for h in history:
            print(f"  ORDSEQ: {h.get('ORDSEQ')} | Date: {h.get('ANEBGNDTTM')}")
            if '2026-02-16' in str(h.get('ANEBGNDTTM')):
                print(f"    *** MATCH FOUND FOR 2026-02-16 ***")
                ordseq = h.get('ORDSEQ')
                print(f"    Fetching Q050 for {ordseq}...")
                charging = c.get_anesthesia_charging_data(ordseq, target_patient)
                if charging:
                    for table, rows in charging.items():
                        if table in ['OPDORDM', 'COMMON_ORDER', 'ANEORDER', 'OCCURENCS']:
                            print(f"\n    --- Table: {table} ({len(rows)} rows) ---")
                            for row in rows:
                                pcode = row.get('PFKEY') or row.get('PFCODE')
                                if pcode and '551' in pcode:
                                    print(f"      FOUND: {pcode} | {row.get('PFNM') or row.get('ORDPROCED')}")
    else:
        print("[-] No history found via SQL.")
