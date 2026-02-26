from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807110"

tables = [
    'COMMON.PAT_EMG_NOTE_ADM',
    'COMMON.PAT_EMG_NOTE_POMR'
]

for t in tables:
    print(f"[*] Probing {t} with ECASENO = {caseno}")
    query = f"SELECT * FROM {t} WHERE ECASENO = '{caseno}'"
    res = c._execute_sql_raw(query)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        print(f"  [+] Found {len(rows)} rows.")
        if rows:
            for k, v in rows[0].items():
                if v: print(f"    {k}: {v}")
    else:
        print("  [-] No data.")
