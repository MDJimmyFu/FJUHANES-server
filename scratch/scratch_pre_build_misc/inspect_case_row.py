from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003600459I"

print(f"[*] Checking PAT_ADM_CASE columns for {target}...")
query = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{target}' AND HCASENO = '46807110'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    if rows:
        print(f"  [!] All Columns: {list(rows[0].keys())}")
        for k, v in rows[0].items():
            print(f"    {k}: {v}")
