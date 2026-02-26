from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807673"

tables = [
    'COMMON.PAT_EMG_TRIAGE',
    'COMMON.PAT_EMG_NOTE_ADM',
    'COMMON.PAT_EMG_NOTE_POMR'
]

for t in tables:
    print(f"[*] Probing {t} for {caseno}...")
    # Triage uses HCASENO, others likely use ECASENO
    ident = 'HCASENO' if 'TRIAGE' in t else 'ECASENO'
    query = f"SELECT * FROM {t} WHERE {ident} = '{caseno}'"
    res = c._execute_sql_raw(query)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        print(f"  [+] Found {len(rows)} rows.")
        if rows:
             # Just show populated clinical columns
             for k, v in rows[0].items():
                 if v and len(str(v)) > 0:
                     print(f"    {k}: {str(v)[:200]}")
    else:
        print("  [-] No data.")
