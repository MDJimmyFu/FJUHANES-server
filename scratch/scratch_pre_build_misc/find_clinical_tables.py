from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

# Search for tables with columns containing "CHIEF" or "ILLNESS" or "PHYSICAL"
keywords = ['CHIEF', 'ILLNESS', 'PHYSICAL', 'EXTREMITIES', 'HEENT', 'CONSCIOUSNESS']
print(f"[*] Searching for tables with columns related to medical notes...")

found_tables = set()
for kw in keywords:
    query = f"SELECT OWNER, TABLE_NAME, COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME LIKE '%{kw}%' AND OWNER IN ('SYSTEM', 'EMGUSR', 'OPDUSR')"
    res = c._execute_sql_raw(query)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        for r in rows:
            print(f"  {r.get('OWNER')}.{r.get('TABLE_NAME')} -> {r.get('COLUMN_NAME')}")
            found_tables.add(f"{r.get('OWNER')}.{r.get('TABLE_NAME')}")

print(f"\n[*] Found {len(found_tables)} potential tables.")
