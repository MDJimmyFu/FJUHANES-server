from his_client_final import HISClient
import sys, re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
hhistnum = "003278373G"

print(f"[*] Inspecting Data for {hhistnum}...")

# 1. Get Cases
sql_case = f"SELECT HCASENO FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhistnum}'"
print(f"[*] Querying PAT_ADM_CASE...")
res1 = c.get_anesthesia_history(hhistnum) # This function does the case lookup internally but returns parsed history. 
# I want to see raw intermediate data, so I'll reproduce the steps manually or use inspection.

# Let's use the client's internal helper if possible, or just re-implement SQL execution here to be safe and verbose.
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

# 1. Get HCASENO
res_case = execute_sql(sql_case)
case_rows = parse_rows(res_case)
cases = [r['HCASENO'] for r in case_rows if 'HCASENO' in r]
print(f"[+] Found {len(cases)} cases: {cases}")

if not cases:
    print("[-] No cases found.")
    sys.exit()

# 2. Get ORRANER (Anesthesia Rows)
case_str = "'" + "','".join(cases) + "'"
sql_or = f"SELECT * FROM OPDUSR.ORRANER WHERE HCASENO IN ({case_str}) AND CANCELYN = 'N'"
res_or = execute_sql(sql_or)
or_rows = parse_rows(res_or)
print(f"[+] Found {len(or_rows)} ORRANER records.")
for r in or_rows:
    print(f"  - ORDSEQ: {r.get('ORDSEQ')} | Date: {r.get('ANEBGNDTTM')} | Method: {r.get('ANENM')}")

# 3. Get OPDORDM (Orders/Procedures)
# Try BOTH HCASENO and OPDCASENO just to be sure
sql_opd = f"SELECT * FROM OPDUSR.OPDORDM WHERE OPDCASENO IN ({case_str}) AND CANCELYN = 'N'"
# Also try HCASENO just in case
# sql_opd_h = f"SELECT * FROM OPDUSR.OPDORDM WHERE HCASENO IN ({case_str}) AND CANCELYN = 'N'"

print(f"[*] Querying OPDORDM (by OPDCASENO)...")
res_opd = execute_sql(sql_opd)
opd_rows = parse_rows(res_opd)
print(f"[+] Found {len(opd_rows)} OPDORDM records.")

# debug print headers of first row
if opd_rows:
    print("Sample OPDORDM Row Keys:", opd_rows[0].keys())

print("\n--- Detailed OPDORDM Check ---")
for r in opd_rows:
    print(f"  - ORDSEQ: {r.get('ORDSEQ')} | Code: {r.get('PFKEY')} | Name: {r.get('PFNM')} | Charge: {r.get('CHARGEFLAG')} | Type: {r.get('ORDTYPE')}")

# Check matching
print("\n--- Matching Analysis (ORRANER vs OPDORDM) ---")
for o in or_rows:
    oseq = o.get('ORDSEQ')
    matches = [m for m in opd_rows if m.get('ORDSEQ') == oseq]
    print(f"ORRANER {oseq}: Found {len(matches)} matches in OPDORDM.")
    for m in matches:
        print(f"    -> Flag: {m.get('CHARGEFLAG')} | Name: {m.get('PFNM')}")
