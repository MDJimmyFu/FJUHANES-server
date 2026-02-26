from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807673"

print(f"[*] Probing Case {cn} in POMR...")
q = f"SELECT * FROM COMMON.PAT_EMG_NOTE_POMR WHERE ECASENO = '{cn}'"
res = c._execute_sql_raw(q)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    print(f"  [+] Found {len(rows)} rows.")
    for r in rows:
        print(f"    - {r}")
else:
    print(f"  [-] No data.")
