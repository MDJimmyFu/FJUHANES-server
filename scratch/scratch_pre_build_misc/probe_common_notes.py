from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807110"

tables = [
    'COMMON.PAT_EMG_NOTE_ADM',
    'COMMON.PAT_EMG_NOTE_POMR',
    'COMMON.PAT_EMG_TRIAGE',
    'COMMON.PAT_EMG_NOTE_DRMEMO',
    'COMMON.PAT_EMG_TRIAGE_PASTHISTORY'
]

for t in tables:
    print(f"[*] Probing {t}...")
    try:
        query = f"SELECT * FROM {t} WHERE CASENO = '{caseno}'"
        res = c._execute_sql_raw(query)
        if res and '<NewDataSet>' in res:
            rows = c._parse_sql_rows_raw(res)
            print(f"  [+] Found {len(rows)} rows.")
            if rows:
                print(f"  [!] Sample Columns: {list(rows[0].keys())}")
                for k, v in rows[0].items():
                    if v: print(f"    {k}: {v}")
        else:
            # Try HCASENO
            query = f"SELECT * FROM {t} WHERE HCASENO = '{caseno}'"
            res = c._execute_sql_raw(query)
            if res and '<NewDataSet>' in res:
                 rows = c._parse_sql_rows_raw(res)
                 print(f"  [+] Found {len(rows)} rows (via HCASENO).")
                 if rows:
                     print(f"  [!] Sample Columns: {list(rows[0].keys())}")
                     for k, v in rows[0].items():
                         if v: print(f"    {k}: {v}")
            else:
                print("  [-] No data.")
    except Exception as e:
        print(f"  [-] Error: {e}")
