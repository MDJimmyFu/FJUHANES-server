from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
targets = ["003617191C", "003600459I", "003380272B", "000639678C"]

opd_case = None
for hhis in targets:
    print(f"[*] Fetching history for {hhis}...")
    hist = []
    try:
        hist = c.get_comprehensive_patient_history(hhis)
    except:
        continue
        
    for h in hist:
        if h['type'] == 'OPD':
            opd_case = h['caseno']
            print(f"  [+] Found OPD Case: {opd_case} (Date: {h['date']}) for {hhis}")
            break
    if opd_case: break

if not opd_case:
    print("[-] No OPD case found. Exiting.")
    sys.exit()

# 2. Search for tables (split queries)
keywords = ['POMR', 'NOTE', 'SOAP']
found_tables = []

for kw in keywords:
    print(f"\n[*] Searching OPDUSR for tables with '{kw}'...")
    q = f"SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = 'OPDUSR' AND TABLE_NAME LIKE '%{kw}%'"
    try:
        res = c._execute_sql_raw(q)
        if res and '<NewDataSet>' in res:
            rows = c._parse_sql_rows_raw(res)
            for r in rows:
                tname = f"OPDUSR.{r['TABLE_NAME']}"
                if tname not in found_tables:
                    found_tables.append(tname)
    except Exception as e:
        print(f"[-] Error querying for {kw}: {e}")

# Explicitly add likely candidates if not found
if 'OPDUSR.INAPOMR' not in found_tables: found_tables.append('OPDUSR.INAPOMR')
if 'OPDUSR.INAPOMRT' not in found_tables: found_tables.append('OPDUSR.INAPOMRT')
if 'OPDUSR.OPD_NOTE' not in found_tables: found_tables.append('OPDUSR.OPD_NOTE')

print(f"\n[*] Probing {len(found_tables)} tables with Case {opd_case}...")

for tname in found_tables:
    try:
        # Check columns to find identifier
        owner, name = tname.split('.')
        q_col = f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = '{owner}' AND TABLE_NAME = '{name}'"
        r_col = c._execute_sql_raw(q_col)
        cols = []
        if r_col and '<NewDataSet>' in r_col:
            cols = [x['COLUMN_NAME'] for x in c._parse_sql_rows_raw(r_col)]
        
        cond = ""
        if 'OPDCASENO' in cols: cond = f"OPDCASENO = '{opd_case}'"
        elif 'CASENO' in cols: cond = f"CASENO = '{opd_case}'"
        elif 'HCASENO' in cols: cond = f"HCASENO = '{opd_case}'"
        
        if cond:
            q_data = f"SELECT * FROM {tname} WHERE {cond}"
            r_data = c._execute_sql_raw(q_data)
            if r_data and '<NewDataSet>' in r_data:
                d_rows = c._parse_sql_rows_raw(r_data)
                print(f"  [+] FOUND DATA in {tname} ({len(d_rows)} rows)")
                # Check for S, O, A, P or similar text
                if d_rows:
                    row = d_rows[0]
                    # Print relevant fields
                    out = {k: str(v)[:50] for k,v in row.items() if v}
                    print(f"    Sample: {out}")
        else:
             print(f"  [-] No identifier in {tname}: {cols}")
             
    except Exception as e:
         print(f"  [-] Error probing {tname}: {e}")
