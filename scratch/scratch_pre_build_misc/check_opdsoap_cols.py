from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
print("[*] Checking columns of OPDUSR.OPDSOAP...")
q = "SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = 'OPDUSR' AND TABLE_NAME = 'OPDSOAP'"
res = c._execute_sql_raw(q)
if res and '<NewDataSet>' in res:
    cols = [r['COLUMN_NAME'] for r in c._parse_sql_rows_raw(res)]
    print(f"  Columns: {cols}")
