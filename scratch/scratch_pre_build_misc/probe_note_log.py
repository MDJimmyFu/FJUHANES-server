from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807673"

query = f"SELECT * FROM COMMON.PAT_EMG_NOTE_LOG WHERE ECASENO = '{caseno}'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    print(f"[+] Found {len(rows)} rows in PAT_EMG_NOTE_LOG.")
    for r in rows:
        print(r)
else:
    print("[-] No data in PAT_EMG_NOTE_LOG.")
