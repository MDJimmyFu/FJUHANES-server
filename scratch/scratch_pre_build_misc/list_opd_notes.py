from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

# Search for tables in OPDUSR with likely names
print("[*] Searching OPDUSR for note tables...")
query = "SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = 'OPDUSR' AND (TABLE_NAME LIKE '%POMR%' OR TABLE_NAME LIKE '%NOTE%' OR TABLE_NAME LIKE '%SOAP%')"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    for r in rows:
        print(f"  OPDUSR.{r['TABLE_NAME']}")
