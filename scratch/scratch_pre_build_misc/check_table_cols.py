from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

tables = ['SYSTEM.PAT_ADM_DRMEMO', 'SYSTEM.PAT_ADM_REPORT']

for t in tables:
    print(f"[*] Table: {t}")
    owner, name = t.split('.')
    query = f"SELECT COLUMN_NAME, DATA_TYPE FROM ALL_TAB_COLUMNS WHERE OWNER = '{owner}' AND TABLE_NAME = '{name}'"
    res = c._execute_sql_raw(query)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        for r in rows:
            print(f"  {r.get('COLUMN_NAME')} ({r.get('DATA_TYPE')})")
