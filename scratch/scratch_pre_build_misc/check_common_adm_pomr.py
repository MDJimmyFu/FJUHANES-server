from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

tables = [
    'COMMON.PAT_ADM_NOTE_POMR',
    'COMMON.PAT_ADM_NOTE_LOG'
]

for t in tables:
    print(f"[*] Checking {t} for Case {cn}...")
    q = f"SELECT * FROM {t} WHERE ECASENO = '{cn}'"
    res = c._execute_sql_raw(q)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        print(f"  [+] Found {len(rows)} rows.")
        for r in rows:
            print(f"    - {r}")
    else:
        print(f"  [-] No data.")
