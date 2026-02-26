from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

# 1. Probe VGHTC.POMR_SOAP
print("[*] Probing VGHTC.POMR_SOAP...")
q_col = "SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = 'VGHTC' AND TABLE_NAME = 'POMR_SOAP'"
res_col = c._execute_sql_raw(q_col)
if res_col and '<NewDataSet>' in res_col:
    cols = [r['COLUMN_NAME'] for r in c._parse_sql_rows_raw(res_col)]
    print(f"  Columns: {cols}")
    cond = ""
    if 'ECASENO' in cols: cond = f"ECASENO = '{cn}'"
    elif 'CASENO' in cols: cond = f"CASENO = '{cn}'"
    
    if cond:
        q = f"SELECT * FROM VGHTC.POMR_SOAP WHERE {cond}"
        res = c._execute_sql_raw(q)
        if res and '<NewDataSet>' in res:
             rows = c._parse_sql_rows_raw(res)
             print(f"  [+] Found {len(rows)} rows in VGHTC.POMR_SOAP.")
             for i, r in enumerate(rows):
                 print(f"    --- Row {i+1} ---")
                 for k, v in r.items():
                     if v: print(f"      {k}: {v}")

# 2. Probe IMSDB EMGROOT -> TEXT
print(f"\n[*] Probing IMSDB.DBEMGEMG_EMGROOT for {cn}...")
q_root = f"SELECT * FROM IMSDB.DBEMGEMG_EMGROOT WHERE EMGCASNO = '{cn}'"
res_root = c._execute_sql_raw(q_root)
if res_root and '<NewDataSet>' in res_root:
    rows = c._parse_sql_rows_raw(res_root)
    print(f"  [+] Found {len(rows)} rows in EMGROOT.")
    if rows:
        # Check what keys we have
        r = rows[0]
        # Try to find a key that links to EMGTEXT
        # Usually it's internal like KFA_EMGROOT, but maybe EMGPRKEY?
        prkey = r.get('EMGPRKEY')
        print(f"    EMGPRKEY: {prkey}")
        
        # Try querying EMGTEXT with this key (guessing column name KFA_EMGROOT or EMGPRKEY)
        # I need to know EMGTEXT columns to guess the join key
        q_text_col = "SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = 'IMSDB' AND TABLE_NAME = 'DBEMGEMG_EMGTEXT'"
        res_text_col = c._execute_sql_raw(q_text_col)
        text_cols = []
        if res_text_col and '<NewDataSet>' in res_text_col:
             text_cols = [x['COLUMN_NAME'] for x in c._parse_sql_rows_raw(res_text_col)]
             print(f"    EMGTEXT Columns: {text_cols}")
             
             # Try to join
             join_col = 'KFA_EMGROOT' if 'KFA_EMGROOT' in text_cols else None
             if not join_col and 'EMGPRKEY' in text_cols: join_col = 'EMGPRKEY'
             
             if join_col and prkey:
                 q_text = f"SELECT * FROM IMSDB.DBEMGEMG_EMGTEXT WHERE {join_col} = '{prkey}'"
                 # Wait, KFA columns are often hidden or system generated?
                 # If KFA_EMGROOT is not in columns list, maybe I assume it exists?
                 # Or maybe the key is something else?
                 
                 # Let's try querying EMGTEXT with whatever join column we found
                 print(f"    Querying EMGTEXT on {join_col} = {prkey}...")
                 res_text = c._execute_sql_raw(q_text)
                 if res_text and '<NewDataSet>' in res_text:
                     t_rows = c._parse_sql_rows_raw(res_text)
                     print(f"    [+] Found textual data!")
                     print(t_rows[0])
