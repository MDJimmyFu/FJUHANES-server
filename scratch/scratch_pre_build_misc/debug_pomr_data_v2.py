from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
cn = "46807040"

print(f"[*] Probing POMR for Case {cn}...")
q_pomr = f"SELECT * FROM COMMON.PAT_EMG_NOTE_POMR WHERE ECASENO = '{cn}'"
res_pomr = c._execute_sql_raw(q_pomr)
if res_pomr and '<NewDataSet>' in res_pomr:
    p_rows = c._parse_sql_rows_raw(res_pomr)
    print(f"    Found {len(p_rows)} progress notes.")
    for i, p in enumerate(p_rows):
        print(f"    --- Note {i+1} ---")
        for k, v in p.items():
            if v: print(f"      {k}: {v}")
else:
    print(f"    [-] No progress notes found for {cn}. Raw response: {res_pomr}")
