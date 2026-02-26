from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

tables = [
    'COMMON.PAT_EMG_NOTE_LOG',
    'COMMON.PAT_EMG_NOTE_DRMEMO',
    'COMMON.PAT_EMG_NOTE_DIS'
]

for t in tables:
    print(f"[*] Probing {t} for Case {cn}...")
    q = f"SELECT * FROM {t} WHERE ECASENO = '{cn}'"
    res = c._execute_sql_raw(q)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        print(f"  [+] Found {len(rows)} rows.")
        for i, r in enumerate(rows):
            print(f"    --- Row {i+1} ---")
            for k, v in r.items():
                if v: print(f"      {k}: {v}")
    else:
        print(f"  [-] No data.")
