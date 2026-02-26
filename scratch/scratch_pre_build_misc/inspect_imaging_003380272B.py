from his_client_final import HISClient
import sys, re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
# Patient 003380272B
ordseq = None # Need to find the latest ordseq or use hhistnum?
# The user didn't specify a date, so let's try to get the surgery list for today or yesterday to find the ORDSEQ, 
# or just query C430 directly if we can (C430 needs ORDSEQ or HHISTNUM).
# The client `get_pre_anesthesia_data` takes (ordseq, hhistnum).
# Let's try to search the surgery list first to get a valid ORDSEQ if possible.

target_hid = "003380272B"
print(f"[*] Inspecting Imaging for {target_hid}...")

# 1. Search Surgery List for ORDSEQ (optional but good for context)
surg_list = c.get_surgery_list("2026-02-18") # Try yesterday/today
found_seq = ""
if surg_list:
    for s in surg_list:
        if target_hid in str(s):
            print(f"[+] Found in surgery list: {s}")
            found_seq = s.get('ORDSEQ')
            break
if not found_seq:
    # Try 2026-02-19
    surg_list = c.get_surgery_list("2026-02-19")
    if surg_list:
        for s in surg_list:
            if target_hid in str(s):
                print(f"[+] Found in surgery list (02-19): {s}")
                found_seq = s.get('ORDSEQ')
                break

if not found_seq:
    print("[-] Could not find patient in surgery list for 02-18 or 02-19. Will try to fetch C430 with just HHISTNUM if possible, or assume an ORDSEQ.")
    # Actually get_pre_anesthesia_data checks if ordseq is provided. If not, it might fail or rely on HHISTNUM only?
    # Looking at his_client_final.py: 
    # def get_pre_anesthesia_data(self, ordseq, hhistnum): ...
    # payload = ... <ORDSEQ>{ordseq}</ORDSEQ> ...
    # If ordseq is missing, it sends empty string. Let's see if C430 responds to just HHISTNUM.
    # But usually C430 needs a specific surgery context.
    pass

# 2. Fetch C430 Data
print(f"[*] Fetching C430 data for {target_hid} (Seq: {found_seq})...")
data = c.get_pre_anesthesia_data(found_seq or "", target_hid)

if not data:
    print("[-] No data returned from C430.")
    sys.exit()

# 3. List ALL Table Names
print(f"[+] Tables in C430: {list(data.keys())}")

# 4. Search for Keywords in ALL Tables
keywords = ['CXR', 'Chest', 'Echo', 'PFT', 'Lung', 'Function', 'WNL', 'Abnormal']
print("\n--- Searching for Imaging Keywords ---")

found_any = False
for table, rows in data.items():
    # Check if table name itself is relevant
    if any(k in table.upper() for k in ['CXR', 'ECHO', 'PFT', 'INSPECT']):
        print(f"\n[!] Table '{table}' might be relevant. ({len(rows)} rows)")
        for i, r in enumerate(rows):
            print(f"  Row {i}: {r}")
        found_any = True
        continue

    # Search content
    for i, r in enumerate(rows):
        row_str = str(r)
        if any(k.upper() in row_str.upper() for k in keywords):
            print(f"\n[?] Found keyword in {table} Row {i}: {r}")
            found_any = True

if not found_any:
    print("[-] No obvious imaging data found.")

# 5. Specifically Dump `INSPECTION` or `INSPECTION_CXR` if they exist but were missed
if 'INSPECTION_CXR' in data:
    print(f"\n--- INSPECTION_CXR Content ---")
    print(data['INSPECTION_CXR'])

if 'INSPECTION' in data:
    print(f"\n--- INSPECTION Content ---")
    print(data['INSPECTION'])

if 'CXR' in data:
    print(f"\n--- CXR Content ---")
    print(data['CXR'])
