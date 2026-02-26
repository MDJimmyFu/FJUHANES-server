from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

# 1. Probe Draft Tables
draft_tables = [
    'COMMON.PAT_EMG_NOTE_ESIGN_UNFIX',
    'COMMON.PAT_EMG_NOTE_ESIGN_TEMP'
]
print(f"[*] Probing Draft Tables for {cn}...")
for t in draft_tables:
    try:
        q = f"SELECT * FROM {t} WHERE ECASENO = '{cn}'"
        res = c._execute_sql_raw(q)
        if res and '<NewDataSet>' in res:
            rows = c._parse_sql_rows_raw(res)
            print(f"  [+] Found {len(rows)} rows in {t}")
            for i, r in enumerate(rows):
                print(f"    --- Row {i+1} ---")
                for k, v in r.items():
                    if v: print(f"      {k}: {v}")
    except Exception as e:
        print(f"  [-] Error checking {t}: {e}")

# 2. Probe IMSDB with LIKE
print(f"\n[*] Probing IMSDB Root with LIKE %{cn}...")
q_root = f"SELECT * FROM IMSDB.DBEMGEMG_EMGROOT WHERE EMGCASNO LIKE '%{cn}'"
res_root = c._execute_sql_raw(q_root)
if res_root and '<NewDataSet>' in res_root:
    rows = c._parse_sql_rows_raw(res_root)
    print(f"  [+] Found {len(rows)} rows in IMSDB Root.")
    if rows:
        r = rows[0]
        # Try to find a key
        prkey = r.get('EMGPRKEY') or r.get('KFA_EMGROOT')
        print(f"    EMGPRKEY/Key: {prkey}")
        
        # Try finding text table
        # We need to know the text table name and join key
        # Assuming DBEMGEMG_EMGTEXT and key is EMGPRKEY or KFA_EMGROOT
        text_table = "IMSDB.DBEMGEMG_EMGTEXT"
        
        # Check columns of text table first to find join key
        q_col = f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = 'IMSDB' AND TABLE_NAME = 'DBEMGEMG_EMGTEXT'"
        res_col = c._execute_sql_raw(q_col)
        cols = []
        if res_col and '<NewDataSet>' in res_col:
             cols = [x['COLUMN_NAME'] for x in c._parse_sql_rows_raw(res_col)]
             
        join_key = 'EMGPRKEY' if 'EMGPRKEY' in cols else 'KFA_EMGROOT'
        
        if prkey:
            q_text = f"SELECT * FROM {text_table} WHERE {join_key} = '{prkey}'"
            print(f"    Querying Text: {q_text}")
            res_text = c._execute_sql_raw(q_text)
            if res_text and '<NewDataSet>' in res_text:
                t_rows = c._parse_sql_rows_raw(res_text)
                print(f"    [!] Found Text Data: {t_rows[0]}")
