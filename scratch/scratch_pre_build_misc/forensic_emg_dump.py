from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

tables = [
    'COMMON.PAT_EMG_NOTE_ADM',
    'COMMON.PAT_EMG_NOTE_POMR',
    'COMMON.PAT_EMG_NOTE_DIS',
    'COMMON.PAT_EMG_TRIAGE'
]

print(f"[*] Forensic dump for Case {cn}...")

for t in tables:
    print(f"\n[*] Querying {t}...")
    try:
        ident = 'HCASENO' if 'TRIAGE' in t else 'ECASENO'
        query = f"SELECT * FROM {t} WHERE {ident} = '{cn}'"
        res = c._execute_sql_raw(query)
        if res and '<NewDataSet>' in res:
            rows = c._parse_sql_rows_raw(res)
            print(f"  [+] Found {len(rows)} rows.")
            for i, r in enumerate(rows):
                print(f"  --- Row {i+1} ---")
                for k, v in r.items():
                    # Print ALL non-empty values
                    if v and str(v).strip(): 
                        print(f"    {k}: {v}")
        else:
            print("  [-] No data.")
    except Exception as e:
        print(f"  [-] Error: {e}")
