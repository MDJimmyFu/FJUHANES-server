from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003617191C"

print(f"[*] Analyzing records for {target}...")
# Find EMG caseno
query = f"SELECT HCASENO, HADMDT, HVDOCNM FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{target}' AND HINCURSVCL = 'EMG'"
res = c._execute_sql_raw(query)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    for r in rows:
        cn = r['HCASENO']
        print(f"\n[+] Case {cn} (Date: {r['HADMDT']}, Doctor: {r['HVDOCNM']})")
        
        # Check POMR note
        q_pomr = f"SELECT * FROM COMMON.PAT_EMG_NOTE_POMR WHERE ECASENO = '{cn}'"
        r_pomr = c._execute_sql_raw(q_pomr)
        if r_pomr and '<NewDataSet>' in r_pomr:
            p_rows = c._parse_sql_rows_raw(r_pomr)
            print(f"    Found {len(p_rows)} progress notes.")
            for i, p in enumerate(p_rows):
                print(f"    --- Note {i+1} ---")
                for k, v in p.items():
                    if v: print(f"      {k}: {v}")
        else:
            print("    [-] No progress notes found.")
else:
    print(f"[-] No EMG records found for {target}")
