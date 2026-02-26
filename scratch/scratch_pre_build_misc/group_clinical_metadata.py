from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807110"

# Maybe I should check PAT_ADM_DRMEMO again but with different columns or just SELECT *
# Also check for columns like 'CC', 'PI', 'PH' (common abbreviations)

keywords = ['CHIEF', 'PRES', 'PAST', 'PHYSICAL', 'COMPLAINT', 'ILLNESS']
all_cols = []
for kw in keywords:
    query = f"SELECT OWNER, TABLE_NAME, COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME LIKE '%{kw}%'"
    res = c._execute_sql_raw(query)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        for r in rows:
            owner = r.get('OWNER')
            if owner in ['SYSTEM', 'EMGUSR', 'OPDUSR']:
                all_cols.append(r)

print(f"[*] Found {len(all_cols)} matching columns in target schemas.")
# Group by table
tables = {}
for r in all_cols:
    tkey = f"{r['OWNER']}.{r['TABLE_NAME']}"
    if tkey not in tables: tables[tkey] = []
    tables[tkey].append(r['COLUMN_NAME'])

for t, cols in tables.items():
    print(f"  {t} -> {cols}")
