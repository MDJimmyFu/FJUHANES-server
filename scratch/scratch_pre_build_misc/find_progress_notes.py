from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807673"

# Search for any table with NOTE or PROGRESS in the name that might have data for this case
query = "SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE (TABLE_NAME LIKE '%PROGRESS%' OR TABLE_NAME LIKE '%NOTE%') AND OWNER IN ('COMMON', 'EMGUSR')"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    tables = c._parse_sql_rows_raw(res)
    for t in tables:
        tname = f"{t['OWNER']}.{t['TABLE_NAME']}"
        # Quickly check if it has columns like ECASENO or HCASENO
        try:
             # Just try a query
             q2 = f"SELECT count(*) as cnt FROM {tname} WHERE ECASENO = '{caseno}' or HCASENO = '{caseno}'"
             r2 = c._execute_sql_raw(q2)
             if r2 and '<NewDataSet>' in r2:
                 cnt = c._parse_sql_rows_raw(r2)[0].get('CNT', 0)
                 if int(cnt) > 0:
                     print(f"[!] Found data in {tname}: {cnt} rows")
        except: continue
