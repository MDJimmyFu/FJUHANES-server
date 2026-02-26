from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003617191C"

print("[*] Columns of COMMON.PAT_EMG_NOTE_POMR:")
query = "SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = 'COMMON' AND TABLE_NAME = 'PAT_EMG_NOTE_POMR'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    cols = [r['COLUMN_NAME'] for r in c._parse_sql_rows_raw(res)]
    print(f"    {cols}")
    
    # Check if HHISNUM exists in this table
    if 'HHISNUM' in cols:
        print(f"[*] Searching by HHISNUM = {target}...")
        q2 = f"SELECT * FROM COMMON.PAT_EMG_NOTE_POMR WHERE HHISNUM = '{target}'"
        r2 = c._execute_sql_raw(q2)
        if r2 and '<NewDataSet>' in r2:
            print(f"    Found {len(c._parse_sql_rows_raw(r2))} rows by HHISNUM.")
    else:
        print("[-] HHISNUM column not found in PAT_EMG_NOTE_POMR.")

print(f"[*] Searching for all entries for Case 46807040...")
q3 = f"SELECT * FROM COMMON.PAT_EMG_NOTE_POMR WHERE ECASENO = '46807040'"
r3 = c._execute_sql_raw(q3)
if r3 and '<NewDataSet>' in r3:
    rows = c._parse_sql_rows_raw(r3)
    for i, r in enumerate(rows):
        print(f"    Note {i+1}: S={r.get('S')}, O={r.get('O')}, A={r.get('A')}, P={r.get('P')}, EXDRMEMO={r.get('EXDRMEMO')}")
