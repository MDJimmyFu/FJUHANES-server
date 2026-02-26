from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
hhis = "003617191C"

# 1. Get an OPD case number
print(f"[*] Fetching history for {hhis}...")
hist = c.get_comprehensive_patient_history(hhis)
opd_case = None
for h in hist:
    if h['type'] == 'OPD':
        opd_case = h['caseno']
        print(f"  Found OPD Case: {opd_case} (Date: {h['date']})")
        break

if not opd_case:
    print("[-] No OPD case found. Exiting.")
    sys.exit()

# 2. Search for tables (split queries)
keywords = ['POMR', 'NOTE', 'SOAP']
for kw in keywords:
    print(f"\n[*] Searching OPDUSR for tables with '{kw}'...")
    q = f"SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = 'OPDUSR' AND TABLE_NAME LIKE '%{kw}%'"
    try:
        res = c._execute_sql_raw(q)
        if res and '<NewDataSet>' in res:
            rows = c._parse_sql_rows_raw(res)
            for r in rows:
                tname = f"OPDUSR.{r['TABLE_NAME']}"
                print(f"  Found: {tname}")
                # Probe this table immediately
                try:
                    # Check columns to find identifier
                    owner, name = "OPDUSR", r['TABLE_NAME']
                    q_col = f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = '{owner}' AND TABLE_NAME = '{name}'"
                    r_col = c._execute_sql_raw(q_col)
                    cols = []
                    if r_col and '<NewDataSet>' in r_col:
                        cols = [x['COLUMN_NAME'] for x in c._parse_sql_rows_raw(r_col)]
                    
                    cond = ""
                    if 'OPDCASENO' in cols: cond = f"OPDCASENO = '{opd_case}'"
                    elif 'CASENO' in cols: cond = f"CASENO = '{opd_case}'"
                    elif 'hCaseno' in cols: cond = f"hCaseno = '{opd_case}'" # sometimes lower case? unlikely in oracle but possible
                    
                    if cond:
                        q_data = f"SELECT * FROM {tname} WHERE {cond}"
                        r_data = c._execute_sql_raw(q_data)
                        if r_data and '<NewDataSet>' in r_data:
                            d_rows = c._parse_sql_rows_raw(r_data)
                            print(f"    [!] FOUND DATA ({len(d_rows)} rows) in {tname}")
                            if d_rows:
                                print(f"    Sample: {d_rows[0]}")
                except Exception as e:
                     print(f"    [-] Error probing {tname}: {e}")

    except Exception as e:
        print(f"[-] Error querying for {kw}: {e}")
