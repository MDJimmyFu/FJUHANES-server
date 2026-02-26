from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno = "46807110"

tables = [
    'SYSTEM.PAT_ADM_DRMEMO',
    'SYSTEM.PAT_ADM_REPORT',
    'EMGUSR.EMGRECORD',
    'EMGUSR.EMGDIAG',
    'EMGUSR.EMGMEDREC',
    'EMGUSR.EMGTriage'
]

for t in tables:
    print(f"[*] Probing {t}...")
    try:
        query = f"SELECT * FROM {t} WHERE OPDCASENO = '{caseno}'"
        if 'SYSTEM' in t:
             query = f"SELECT * FROM {t} WHERE HCASENO = '{caseno}'"
        
        res = c._execute_sql_raw(query)
        if res and '<NewDataSet>' in res:
            rows = c._parse_sql_rows_raw(res)
            print(f"  [+] Found {len(rows)} rows.")
            if rows:
                print(f"  [!] Sample Columns: {list(rows[0].keys())}")
                # Print some content
                for k, v in rows[0].items():
                    if v and len(str(v)) > 0:
                        print(f"    {k}: {v}")
        else:
            print("  [-] No data.")
    except Exception as e:
        print(f"  [-] Error: {e}")
