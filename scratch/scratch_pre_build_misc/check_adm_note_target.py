from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003617191C"

query = f"SELECT * FROM COMMON.PAT_EMG_NOTE_ADM WHERE HHISNUM = '{target}'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    for r in rows:
        print(f"--- ADM NOTE for {target} ---")
        for k, v in r.items():
            if v: print(f"  {k}: {v}")
else:
    print(f"[-] No ADM note found for {target}")
