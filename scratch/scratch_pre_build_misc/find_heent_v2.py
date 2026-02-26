from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

target_schemas = ['COMMON', 'OPDUSR', 'IMSDB', 'SYSTEM', 'VGHTC']

print(f"[*] Searching for HEENT column in schemas: {target_schemas}")

for owner in target_schemas:
    try:
        q = f"SELECT TABLE_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = '{owner}' AND COLUMN_NAME = 'HEENT'"
        res = c._execute_sql_raw(q)
        if res and '<NewDataSet>' in res:
            tables = [r['TABLE_NAME'] for r in c._parse_sql_rows_raw(res)]
            print(f"  [{owner}] Found HEENT column in: {tables}")
            
            for tname in tables:
                full_name = f"{owner}.{tname}"
                # Probe this table for our case
                try:
                     # Check indentifier
                     q_col = f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = '{owner}' AND TABLE_NAME = '{tname}'"
                     r_col = c._execute_sql_raw(q_col)
                     cols = [x['COLUMN_NAME'] for x in c._parse_sql_rows_raw(r_col)]
                     
                     cond = ""
                     if 'ECASENO' in cols: cond = f"ECASENO = '{cn}'"
                     elif 'HCASENO' in cols: cond = f"HCASENO = '{cn}'"
                     elif 'CASENO' in cols: cond = f"CASENO = '{cn}'"
                     elif 'ENCOUNTER_ID' in cols: cond = f"ENCOUNTER_ID = '{cn}'"
                     elif 'OPDCASENO' in cols: cond = f"OPDCASENO = '{cn}'"

                     if cond:
                         q_data = f"SELECT * FROM {full_name} WHERE {cond}"
                         r_data = c._execute_sql_raw(q_data)
                         if r_data and '<NewDataSet>' in r_data:
                             rows = c._parse_sql_rows_raw(r_data)
                             if rows:
                                 val = rows[0].get('HEENT', '')
                                 print(f"    [!] FOUND DATA in {full_name}!")
                                 print(f"    HEENT: '{val}'")
                                 if val: print(f"    [!!!] SUCCESS! DATA FOUND IN {full_name}")
                except Exception as e:
                    print(f"    [-] Error checking {full_name}: {e}")
    except Exception as ex:
        print(f"  [-] Error querying schema {owner}: {ex}")
