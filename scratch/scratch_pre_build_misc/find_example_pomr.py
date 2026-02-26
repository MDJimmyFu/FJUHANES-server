from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

print("[*] Searching for ANY populated SOAP notes in COMMON.PAT_EMG_NOTE_POMR...")
# We use length check or IS NOT NULL
q = "SELECT * FROM (SELECT * FROM COMMON.PAT_EMG_NOTE_POMR WHERE S IS NOT NULL OR O IS NOT NULL OR A IS NOT NULL OR P IS NOT NULL) WHERE ROWNUM <= 5"
res = c._execute_sql_raw(q)
if res and '<NewDataSet>' in res:
    rows = c._parse_sql_rows_raw(res)
    print(f"    Found {len(rows)} populated rows.")
    for r in rows:
        print(f"    - ECASENO: {r.get('ECASENO')} | S: {r.get('S')}")
else:
    print("    [-] No populated POMR strings found via IS NOT NULL.")

# Try searching for empty string check
q2 = "SELECT * FROM (SELECT * FROM COMMON.PAT_EMG_NOTE_POMR WHERE length(S) > 0) WHERE ROWNUM <= 5"
res2 = c._execute_sql_raw(q2)
if res2 and '<NewDataSet>' in res2:
    rows = c._parse_sql_rows_raw(res2)
    print(f"    Found {len(rows)} rows with length(S) > 0.")
else:
    print("    [-] No populated POMR strings found via length(S) > 0.")
