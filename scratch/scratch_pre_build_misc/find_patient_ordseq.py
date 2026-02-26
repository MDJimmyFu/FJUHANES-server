from his_client_final import HISClient
import json
import datetime

client = HISClient()
target_hhistnum = "003617083J"

# Try today and maybe +/- 1 day if not found, but start with today or default
print(f"Searching for {target_hhistnum} in surgery list...")
# We'll fetch today's list. If user is looking at a different date, I might miss it, 
# but let's assume it's fresh.
data = client.get_surgery_list() 

found = None
for item in data:
    # Check both keys just in case
    hhn = item.get('HHISTNUM') or item.get('HhistNum')
    if hhn == target_hhistnum:
        found = item
        break

if found:
    print("Found Patient:")
    print(json.dumps(found, indent=2, ensure_ascii=False))
    ordseq = found.get('ORDSEQ') or found.get('OrdSeq')
    print(f"\nORDSEQ: {ordseq}")
else:
    print(f"Patient {target_hhistnum} not found in today's list.")
