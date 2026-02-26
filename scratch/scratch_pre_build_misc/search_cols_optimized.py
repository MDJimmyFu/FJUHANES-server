from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

# Short queries to avoid length limit
kw_list = ['CHIEF', 'PRES', 'PAST', 'PHYS', 'PROG', 'ILLNESS']

for kw in kw_list:
    print(f"[*] Keyword: {kw}")
    query = f"SELECT OWNER, TABLE_NAME, COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME LIKE '%{kw}%'"
    # Filter owners in script to save SQL length
    res = c._execute_sql_raw(query)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        for r in rows:
            owner = r.get('OWNER')
            if owner in ['SYSTEM', 'EMGUSR', 'OPDUSR']:
                print(f"  {owner}.{r.get('TABLE_NAME')} -> {r.get('COLUMN_NAME')}")
