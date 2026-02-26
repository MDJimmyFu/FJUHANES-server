from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"
hhis = "003617191C"

# 1. Check length of columns in PAT_EMG_NOTE_ADM
print(f"[*] Checking column lengths for Case {cn}...")
query = f"SELECT length(HEENT) as L_HEENT, length(PRESENT_ILLNESS) as L_PI, length(CHIEF_COMPLAINTS) as L_CC FROM COMMON.PAT_EMG_NOTE_ADM WHERE ECASENO = '{cn}'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    for r in rows:
        print(f"  Lengths: {r}")

# 2. Check for other EMG visits
print(f"\n[*] Checking all EMG visits for {hhis}...")
q2 = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhis}' AND HINCURSVCL = 'EMG'"
r2 = c._execute_sql_raw(q2)
if r2 and '<NewDataSet>' in r2:
    rows = c._parse_sql_rows_raw(r2)
    print(f"  [+] Found {len(rows)} visits.")
    for r in rows:
        print(f"  - Case {r['HCASENO']} Date: {r['HADMDT']}")
