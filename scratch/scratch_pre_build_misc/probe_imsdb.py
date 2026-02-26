from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

tables = [
    'IMSDB.DBEMGEMG_EMGTEXT',
    'IMSDB.DBEMGPUR_EMGTEXT',
    'IMSDB.DBEMGEMG_EMGDATA',
    'IMSDB.DBEMGPUR_EMGDATA',
    'SYSTEM.PAT_ADM_DRMEMO'
]

print(f"[*] Probing IMSDB/SYSTEM for Case {cn}...")

for t in tables:
    print(f"\n[*] Querying {t}...")
    try:
        # IMSDB might use different column names like CASENO or HCASENO
        # I'll try generic SELECT * first, but mapped to a variable condition if needed
        # Actually I don't know the column name. Let's try ECASENO first, then HCASENO.
        
        # First find columns to know identifier
        owner, name = t.split('.')
        q_col = f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = '{owner}' AND TABLE_NAME = '{name}'"
        res_col = c._execute_sql_raw(q_col)
        cols = []
        if res_col and '<NewDataSet>' in res_col:
            cols = [r['COLUMN_NAME'] for r in c._parse_sql_rows_raw(res_col)]
        
        cond = ""
        if 'ECASENO' in cols: cond = f"ECASENO = '{cn}'"
        elif 'HCASENO' in cols: cond = f"HCASENO = '{cn}'"
        elif 'CASENO' in cols: cond = f"CASENO = '{cn}'"
        elif 'OPDCASENO' in cols: cond = f"OPDCASENO = '{cn}'"
        
        if cond:
            query = f"SELECT * FROM {t} WHERE {cond}"
            res = c._execute_sql_raw(query)
            if res and '<NewDataSet>' in res:
                rows = c._parse_sql_rows_raw(res)
                print(f"  [+] Found {len(rows)} rows.")
                for i, r in enumerate(rows):
                    print(f"  --- Row {i+1} ---")
                    for k, v in r.items():
                         if v and str(v).strip(): print(f"    {k}: {v}")
            else:
                print("  [-] No data.")
        else:
             print(f"  [-] Could not determine case column from {cols}")

    except Exception as e:
        print(f"  [-] Error: {e}")
