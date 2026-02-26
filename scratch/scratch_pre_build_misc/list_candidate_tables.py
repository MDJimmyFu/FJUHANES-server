from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

# List tables in EMGUSR and SYSTEM starting with PAT_ADM
print(f"[*] Listing target tables...")

schemas = ['EMGUSR', 'SYSTEM']
for s in schemas:
    query = f"SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = '{s}'"
    res = c._execute_sql_raw(query)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        print(f"\n[{s}] Tables:")
        for r in rows:
            tn = r.get('TABLE_NAME')
            if 'MEMO' in tn or 'NOTE' in tn or 'DIAG' in tn or 'RECO' in tn or 'ADM' in tn:
                print(f"  {tn}")
