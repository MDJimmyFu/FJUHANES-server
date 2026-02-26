from his_client_final import HISClient
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
# Use a patient known to have history
target_ordseq = "E46769755OR0001" # This was from the probe earlier
target_hhistnum = "003380272B"

print(f"[*] Dumping C430 tables for {target_hhistnum} / {target_ordseq}...")
data = c.get_pre_anesthesia_data(target_ordseq, target_hhistnum)

if data:
    print(f"[+] Found {len(data)} tables in C430 response:")
    for table_name, rows in data.items():
        print(f"  - {table_name}: {len(rows)} rows")
        if rows:
            print(f"    Sample Keys: {rows[0].keys()}")
            # Print a few rows if it's DIAG or DRUG or CONSULT
            if "DIAG" in table_name or "DRUG" in table_name or "CONSULT" in table_name or "ORDER" in table_name:
                for r in rows[:2]:
                    print(f"    Data: {r}")
else:
    print("[-] No data returned from C430.")
