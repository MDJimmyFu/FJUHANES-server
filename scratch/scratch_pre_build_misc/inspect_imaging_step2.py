from his_client_final import HISClient
import sys, re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003380272B"
print(f"[*] Finding ORDSEQ for {target}...")

# 1. Get Cases
# Use EXM SQL helper directly
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

# Get latest case
q_case = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{target}' ORDER BY HADMDT DESC"
res_case = execute_sql(q_case)
rows_case = parse_rows(res_case)

if not rows_case:
    print("[-] No cases found.")
    sys.exit()

latest_case = rows_case[0]
hcaseno = latest_case.get('HCASENO')
print(f"[+] Latest Case: {hcaseno} from {latest_case.get('HADMDT')}")

# Get ORDSEQ from ORRANER
q_or = f"SELECT * FROM OPDUSR.ORRANER WHERE HCASENO = '{hcaseno}' AND CANCELYN = 'N' ORDER BY ANEBGNDTTM DESC"
res_or = execute_sql(q_or)
rows_or = parse_rows(res_or)

if not rows_or:
    print("[-] No ORRANER records for latest case.")
    # Try OPDORDM
    q_opd = f"SELECT * FROM OPDUSR.OPDORDM WHERE OPDCASENO = '{hcaseno}' AND CANCELYN = 'N'"
    res_opd = execute_sql(q_opd)
    rows_opd = parse_rows(res_opd)
    if rows_opd:
        ordseq = rows_opd[0].get('ORDSEQ')
        print(f"[+] Found ORDSEQ from OPDORDM: {ordseq}")
    else:
        print("[-] No ORDSEQ found. Cannot query C430.")
        sys.exit()
else:
    ordseq = rows_or[0].get('ORDSEQ')
    print(f"[+] Found ORDSEQ from ORRANER: {ordseq}")

# Now query C430 with this ORDSEQ
print(f"[*] Fetching C430 for {ordseq}...")
data = c.get_pre_anesthesia_data(ordseq, target)

# Search for Imaging
if data:
    print(f"[+] All Tables: {list(data.keys())}")
    
    targets = ['INSPECT', 'CXR', 'ECHO', 'PFT', 'REPORT', 'LUNG', 'HEART', 'SONO']
    
    for table, rows in data.items():
        if any(t in table.upper() for t in targets):
            print(f"\n[!] Target Table Found: '{table}' ({len(rows)} rows)")
            for i, r in enumerate(rows):
                print(f"  Row {i}: {r}")
                if i >= 50: 
                    print("  ... (truncated)")
                    break
else:
    print("[-] C430 returned no data.")
