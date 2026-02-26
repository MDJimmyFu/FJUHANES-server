from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

# 1. Search for tables with HEENT column
print("[*] Searching for tables with HEENT column...")
q = "SELECT OWNER, TABLE_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME = 'HEENT' AND OWNER IN ('COMMON', 'OPDUSR', 'IMSDB', 'SYSTEM', 'VGHTC')"
res = c._execute_sql_raw(q)
if res and '<NewDataSet>' in res:
    tables = c._parse_sql_rows_raw(res)
    for t in tables:
        tname = f"{t['OWNER']}.{t['TABLE_NAME']}"
        print(f"  Checking {tname}...")
        
        # Probe this table for our case
        # Try likely identifiers
        try:
             # First check columns to know correct ID
             q_col = f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = '{t['OWNER']}' AND TABLE_NAME = '{t['TABLE_NAME']}'"
             r_col = c._execute_sql_raw(q_col)
             cols = [x['COLUMN_NAME'] for x in c._parse_sql_rows_raw(r_col)]
             
             cond = ""
             if 'ECASENO' in cols: cond = f"ECASENO = '{cn}'"
             elif 'HCASENO' in cols: cond = f"HCASENO = '{cn}'"
             elif 'CASENO' in cols: cond = f"CASENO = '{cn}'"
             elif 'ENCOUNTER_ID' in cols: cond = f"ENCOUNTER_ID = '{cn}'"
             
             if cond:
                 q_data = f"SELECT * FROM {tname} WHERE {cond}"
                 r_data = c._execute_sql_raw(q_data)
                 if r_data and '<NewDataSet>' in r_data:
                     rows = c._parse_sql_rows_raw(r_data)
                     if rows:
                         print(f"    [!] FOUND DATA in {tname}!")
                         # Check if HEENT is populated
                         val = rows[0].get('HEENT')
                         print(f"    HEENT: {val}")
                         if val: print("    [!!!] HEENT IS POPULATED HERE!")
                 else:
                     print("    [-] No data.")
             else:
                 print(f"    [-] No known identifier column in {cols}")
        except Exception as e:
            print(f"    [-] Error: {e}")
