from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

# Search for tables with 'EMG' or 'PAT_ADM' in any schema
query = "SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME LIKE '%EMG%' OR TABLE_NAME LIKE 'PAT_ADM%'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    for r in rows:
        print(f"{r.get('OWNER')}.{r.get('TABLE_NAME')}")
