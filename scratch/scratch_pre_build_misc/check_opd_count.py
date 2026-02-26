from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
case = "46402990"
print(f"[*] Checking OPDSOAP count for {case}...")
q = f"SELECT count(*) as cnt FROM OPDUSR.OPDSOAP WHERE OPDCASENO='{case}'"
res = c._execute_sql_raw(q)
if res:
    rows = c._parse_sql_rows_raw(res)
    print(f"OPDSOAP: {rows}")

q2 = f"SELECT count(*) as cnt FROM OPDUSR.DITTOSOAP WHERE OPDCASENO='{case}'"
res2 = c._execute_sql_raw(q2)
if res2:
    rows2 = c._parse_sql_rows_raw(res2)
    print(f"DITTOSOAP: {rows2}")
