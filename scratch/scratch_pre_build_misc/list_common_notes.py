from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

# Search for tables with 'NOTE' in COMMON schema
query = "SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = 'COMMON' AND TABLE_NAME LIKE '%NOTE%'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    for r in rows:
        print(r.get('TABLE_NAME'))
