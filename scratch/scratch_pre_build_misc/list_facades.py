from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

# Search ALL_OBJECTS for Facades
query = "SELECT OBJECT_NAME FROM ALL_OBJECTS WHERE OBJECT_NAME LIKE 'HISOrm%Facade'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    for r in rows:
        print(r.get('OBJECT_NAME'))
