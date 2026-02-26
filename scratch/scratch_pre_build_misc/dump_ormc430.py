from his_client_final import HISClient
import json

client = HISClient()

# Patient from found_record.txt:
# ORDSEQ = A75176986OR0041
# HHISTNUM = 003617083J

ordseq = 'A75176986OR0041'
hhistnum = '003617083J'

print(f"Fetching ORMC430 for {ordseq} / {hhistnum}...")
data = client.get_pre_anesthesia_data(ordseq, hhistnum)

if data:
    print(f"[+] Got data! Keys: {list(data.keys())[:30]}")
    
    # Look for LAB_DATA related keys
    lab_keys = [k for k in data.keys() if 'LAB' in k.upper() or 'WBC' in k.upper() or 'HB' in k.upper() or 'PLT' in k.upper()]
    print(f"\n[+] Lab-related keys: {lab_keys}")
    
    # Dump all keys and values to file
    with open("ormc430_full_dump.txt", "w", encoding="utf-8") as f:
        for k, v in data.items():
            f.write(f"{k}: {v}\n")
    print(f"\n[+] Full dump written to ormc430_full_dump.txt ({len(data)} keys)")
    
    # Print lab-related values
    for k in lab_keys:
        print(f"  {k}: {data[k]}")
else:
    print("[-] No data returned.")
