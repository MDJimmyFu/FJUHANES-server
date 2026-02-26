from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

query = f"SELECT * FROM SYSTEM.PAT_ADM_NOTE_POMR WHERE ECASENO = '{cn}'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    print(f"[+] Found {len(rows)} rows in SYSTEM.PAT_ADM_NOTE_POMR.")
    for r in rows:
        print(r)
else:
    # Try HCASENO
    query = f"SELECT * FROM SYSTEM.PAT_ADM_NOTE_POMR WHERE HCASENO = '{cn}'"
    res = c._execute_sql_raw(query)
    if res and '<NewDataSet>' in res:
         rows = c._parse_sql_rows_raw(res)
         print(f"[+] Found {len(rows)} rows (via HCASENO) in SYSTEM.PAT_ADM_NOTE_POMR.")
         for r in rows:
             print(r)
    else:
        print("[-] No data in SYSTEM.PAT_ADM_NOTE_POMR.")
