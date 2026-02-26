from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
hhis = "003617191C"
cn = "46807040"

# 1. Search for all rows in ADM note by HHISNUM
print(f"[*] Searching ADM note by HHISNUM {hhis}...")
q = f"SELECT ECASENO, CREATEDT, length(HEENT) as L_HEENT FROM COMMON.PAT_EMG_NOTE_ADM WHERE HHISNUM = '{hhis}'"
res = c._execute_sql_raw(q)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    print(f"  [+] Found {len(rows)} rows.")
    for r in rows:
        print(r)

# 2. Check POMR length
print(f"\n[*] Checking POMR length for {cn}...")
q2 = f"SELECT length(S) as LS, length(O) as LO, length(A) as LA, length(P) as LP FROM COMMON.PAT_EMG_NOTE_POMR WHERE ECASENO = '{cn}'"
r2 = c._execute_sql_raw(q2)
if r2 and '<NewDataSet>' in r2:
    rows = c._parse_sql_rows_raw(r2)
    for r in rows:
        print(r)
