from his_client_final import HISClient
import json

client = HISClient()

ordseq = 'A75176986OR0041'
hhistnum = '003617083J'

print(f"Fetching ORMC430 for {ordseq} / {hhistnum}...")
data = client.get_pre_anesthesia_data(ordseq, hhistnum)

if data:
    print(f"[+] Got data! Keys: {list(data.keys())}")
    
    # Inspect PAT_ADM_DRMEMO records
    memos = data.get('PAT_ADM_DRMEMO', [])
    print(f"\n[+] PAT_ADM_DRMEMO records: {len(memos)}")
    for i, memo in enumerate(memos):
        print(f"\n--- Memo {i+1} ---")
        for k, v in memo.items():
            if v:
                print(f"  {k}: {v[:200] if len(str(v)) > 200 else v}")
    
    # Inspect ORRANER records
    orraner = data.get('ORRANER', [])
    print(f"\n[+] ORRANER records: {len(orraner)}")
    for i, rec in enumerate(orraner[:3]):
        print(f"\n--- ORRANER {i+1} ---")
        for k, v in rec.items():
            if v:
                print(f"  {k}: {v[:200] if len(str(v)) > 200 else v}")
else:
    print("[-] No data returned.")
