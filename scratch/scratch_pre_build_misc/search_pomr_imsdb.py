from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

# 1. Search for POMR tables
print("[*] Searching for tables with POMR in name...")
q_pomr = "SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME LIKE '%POMR%'"
res_pomr = c._execute_sql_raw(q_pomr)
if res_pomr and '<NewDataSet>' in res_pomr:
    rows = c._parse_sql_rows_raw(res_pomr)
    for r in rows:
        print(f"  {r['OWNER']}.{r['TABLE_NAME']}")

# 2. Probe IMSDB Root
tables_root = ['IMSDB.DBEMGEMG_EMGROOT', 'IMSDB.DBEMGPUR_EMGROOT', 'IMSDB.DBEMGPUR_ARC_EMGROOT']
print(f"\n[*] Probing IMSDB Root tables for Case {cn}...")

for t in tables_root:
    # Check columns first
    owner, name = t.split('.')
    q_col = f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = '{owner}' AND TABLE_NAME = '{name}'"
    res_col = c._execute_sql_raw(q_col)
    if res_col and '<NewDataSet>' in res_col:
        cols = [r['COLUMN_NAME'] for r in c._parse_sql_rows_raw(res_col)]
        # Look for likely identifiers
        cond = ""
        if 'ECASENO' in cols: cond = f"ECASENO = '{cn}'"
        elif 'HCASENO' in cols: cond = f"HCASENO = '{cn}'"
        elif 'CASENO' in cols: cond = f"CASENO = '{cn}'"
        elif 'ER_CASENO' in cols: cond = f"ER_CASENO = '{cn}'"
        
        if cond:
            q = f"SELECT * FROM {t} WHERE {cond}"
            res = c._execute_sql_raw(q)
            if res and '<NewDataSet>' in res:
                rows = c._parse_sql_rows_raw(res)
                print(f"  [+] Found {len(rows)} rows in {t}")
                if rows:
                    print(f"    Key: {rows[0].get('KFA_EMGROOT')} / {rows[0].get('EMGROOT')}")
                    # If found, try to query text
                    root_key = rows[0].get('KFA_EMGROOT') or rows[0].get('EMGROOT')
                    if root_key:
                        # Try text table
                        text_table = t.replace('GROOT', 'TEXT')
                        q_text = f"SELECT * FROM {text_table} WHERE KFA_EMGROOT = '{root_key}'"
                        res_text = c._execute_sql_raw(q_text)
                        if res_text and '<NewDataSet>' in res_text:
                            t_rows = c._parse_sql_rows_raw(res_text)
                            print(f"    [!] Found text data in {text_table}!")
                            print(f"    Content: {t_rows[0]}")
        else:
            print(f"  [-] No case column in {t}: {cols}")
