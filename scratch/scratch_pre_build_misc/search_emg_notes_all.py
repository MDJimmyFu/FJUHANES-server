from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

# List all tables in COMMON starting with PAT_EMG_NOTE_
query = "SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = 'COMMON' AND TABLE_NAME LIKE 'PAT_EMG_NOTE_%'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    tables = c._parse_sql_rows_raw(res)
    for t in tables:
        tname = f"COMMON.{t['TABLE_NAME']}"
        try:
            q2 = f"SELECT count(*) as cnt FROM {tname} WHERE ECASENO = '{cn}'"
            r2 = c._execute_sql_raw(q2)
            if r2 and '<NewDataSet>' in r2:
                cnt = int(c._parse_sql_rows_raw(r2)[0].get('CNT', 0))
                if cnt > 0:
                    print(f"[!] Found {cnt} rows in {tname}")
                    q3 = f"SELECT * FROM {tname} WHERE ECASENO = '{cn}'"
                    r3 = c._execute_sql_raw(q3)
                    rows = c._parse_sql_rows_raw(r3)
                    for r in rows:
                        print(f"    - Content: {r}")
        except: continue
