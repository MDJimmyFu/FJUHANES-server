from his_client_final import HISClient
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003380272B"
ordseq = "AA0304381OR1032" # Found in previous step

print(f"[*] Fetching C430 for {ordseq}...")
data = c.get_pre_anesthesia_data(ordseq, target)

if data:
    for table in data.keys():
        rows = data[table]
        if len(rows) > 0:
            # Check if this table has PFTYPE
            if 'PFTYPE' in rows[0]:
                print(f"[!] Found table with PFTYPE: '{table}' ({len(rows)} rows)")
                # Print unique PFTYPEs
                types = set(r.get('PFTYPE') for r in rows)
                print(f"    Types: {types}")
else:
    print("[-] No data.")
