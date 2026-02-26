from his_client_final import HISClient
import json

client = HISClient()
# Patient 003617083J
primary_ordseq = 'A75176986OR0041'
hhistnum = '003617083J'

print(f"[*] Fetching Q050 for {primary_ordseq} to find other ORDSEQs...")
charging = client.get_anesthesia_charging_data(primary_ordseq, hhistnum)

if not charging:
    print("No Q050 data found.")
    exit()

candidates = set()
candidates.add(primary_ordseq)

# Extract from OPDORDM
if 'OPDORDM' in charging:
    for item in charging['OPDORDM']:
        if 'ORDSEQ' in item:
            candidates.add(item['ORDSEQ'])

print(f"[*] Found {len(candidates)} candidate ORDSEQs.")
print(f"Candidates: {sorted(list(candidates))}")

# Try each
for seq in sorted(list(candidates)):
    print(f"\n[*] Trying C430 with ORDSEQ: {seq} ...")
    data = client.get_pre_anesthesia_data(seq, hhistnum)
    
    if data and 'VITALSIGN_HEIGHT' in data and len(data['VITALSIGN_HEIGHT']) > 0:
        print(f"!!! FOUND DATA with {seq} !!!")
        print(json.dumps(data.get('VITALSIGN_HEIGHT', [])[:1], indent=2, ensure_ascii=False))
        print("This is the correct ORDSEQ for Vitals.")
        break
    else:
        print(f"    No VITALSIGN_HEIGHT in {seq}")
