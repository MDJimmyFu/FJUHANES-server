from his_client_final import HISClient
import json, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
surgeries = c.get_surgery_list()
if not surgeries:
    print("[-] No surgeries found.")
    exit()

# Find a patient with charging data
for s in surgeries[:5]:
    ordseq = s['ORDSEQ']
    hhistnum = s['HHISTNUM']
    print(f"\n[*] Trying {ordseq} / {hhistnum}...")
    charging = c.get_anesthesia_charging_data(ordseq, hhistnum)
    if charging and 'OPDORDM' in charging and charging['OPDORDM']:
        print(f"[+] Found OPDORDM with {len(charging['OPDORDM'])} items.")
        # Print all keys of first item
        first = charging['OPDORDM'][0]
        print(f"Keys: {list(first.keys())}")
        # Print all items focusing on materials (M prefix)
        print("\n--- All OPDORDM items ---")
        for item in charging['OPDORDM']:
            code = item.get('PFKEY', '')
            name = item.get('PFNM', '')
            dose = item.get('DOSE', '')
            price = item.get('PFPRICE', item.get('UNITPRICE', item.get('PRICE', '')))
            total = item.get('TOTAL', item.get('TOTALPRICE', ''))
            print(f"  {code:<12} | {name:<40} | qty={dose} | price={price} | total={total}")
        
        # Print the first item full dump
        print("\n--- First OPDORDM item (full) ---")
        print(json.dumps(first, indent=4, ensure_ascii=False))
        
        # Also check if there are materials
        materials = [i for i in charging['OPDORDM'] if i.get('PFKEY', '').startswith('M')]
        if materials:
            print(f"\n--- Material items (M prefix): {len(materials)} ---")
            print(json.dumps(materials[0], indent=4, ensure_ascii=False))
        break
    else:
        print("  No OPDORDM data.")
