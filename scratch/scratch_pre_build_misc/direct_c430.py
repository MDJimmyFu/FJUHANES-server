from his_client_final import HISClient
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

client = HISClient()

targets = [
    {'hhistnum': '003617083J', 'ordseq': 'A75176986OR0041'},
    {'hhistnum': '003509917D', 'ordseq': 'A75177038OR0007'}
]

for t in targets:
    hhistnum = t['hhistnum']
    ordseq = t['ordseq']
    print(f"\n--- Checking {hhistnum} (ORDSEQ: {ordseq}) ---")
    data = client.get_pre_anesthesia_data(ordseq, hhistnum)
    if not data:
        print("    [-] No data returned from C430.")
        continue
        
    tables = list(data.keys())
    print(f"    Tables returned: {tables}")
    
    if 'INSPECTION' in data:
        print(f"    [FOUND] INSPECTION table exists! Count: {len(data['INSPECTION'])}")
        # Print first few rows
        for i, row in enumerate(data['INSPECTION'][:10]):
            print(f"      {i}: {row}")
    else:
        print("    [-] INSPECTION table is MISSING from the response.")
