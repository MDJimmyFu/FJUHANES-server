from his_client_final import HISClient
import json
import datetime
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

client = HISClient()
target_hhistnums = ['003617083J', '003509917D']

# Check a wider range of dates
base_date = datetime.date(2026, 2, 10)
dates = [(base_date + datetime.timedelta(days=x)).strftime('%Y%m%d') for x in range(12)]

found_ordseqs = {pat: set() for pat in target_hhistnums}

print(f"[*] Searching surgery list from {dates[0]} to {dates[-1]}...")

for d in dates:
    print(f"  - Checking {d}...", end='\r')
    surgeries = client.get_surgery_list(d)
    if not surgeries: continue
    
    for s in surgeries:
        pat = s.get('patient')
        if pat in target_hhistnums:
            print(f"  [FOUND] Patient {pat} on {d} -> ORDSEQ: {s.get('ordseq')}")
            found_ordseqs[pat].add(s.get('ordseq'))

print("\n[*] Starting deep C430 inspection...")

for pat, ordseqs in found_ordseqs.items():
    print(f"\n{'='*40}")
    print(f" Patient: {pat}")
    print(f"{'='*40}")
    
    if not ordseqs:
        print("[-] No ORDSEQs found in this date range.")
        continue
        
    for ordseq in ordseqs:
        print(f"\n>>> Querying C430 for ORDSEQ: {ordseq}")
        pre = client.get_pre_anesthesia_data(ordseq, pat)
        if pre:
            tables = list(pre.keys())
            print(f"    Tables found: {tables}")
            if 'INSPECTION' in pre:
                print(f"    [!!!] INSPECTION TABLE FOUND for {ordseq}!")
                print(f"    Rows: {len(pre['INSPECTION'])}")
                for row in pre['INSPECTION']:
                    print(f"      - {row.get('TITLE')}: {row.get('SYB_VALUE')} ({row.get('SIGNDATE')})")
            else:
                print(f"    [-] No INSPECTION table in this ORDSEQ.")
        else:
            print(f"    [-] No data returned from C430 for {ordseq}.")

