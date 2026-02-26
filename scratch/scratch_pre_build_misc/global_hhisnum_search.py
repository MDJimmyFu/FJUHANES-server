from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003617191C"

# Find all tables with HHISNUM column
query = f"SELECT OWNER, TABLE_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME = 'HHISNUM' AND OWNER IN ('SYSTEM', 'COMMON', 'EMGUSR', 'OPDUSR')"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    tables = c._parse_sql_rows_raw(res)
    for t in tables:
        tname = f"{t['OWNER']}.{t['TABLE_NAME']}"
        try:
             q2 = f"SELECT count(*) as cnt FROM {tname} WHERE HHISNUM = '{target}'"
             r2 = c._execute_sql_raw(q2)
             if r2 and '<NewDataSet>' in r2:
                 cnt = int(c._parse_sql_rows_raw(r2)[0].get('CNT', 0))
                 if cnt > 0:
                     print(f"[!] Found data in {tname}: {cnt} rows")
                     # If it's a note table, show a sample
                     if 'NOTE' in tname or 'POMR' in tname:
                         q3 = f"SELECT * FROM {tname} WHERE HHISNUM = '{target}'"
                         r3 = c._execute_sql_raw(q3)
                         rows = c._parse_sql_rows_raw(r3)
                         for r in rows:
                             print(f"    - Content: {r}")
        except: continue
