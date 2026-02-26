from his_client_final import HISClient
import json, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
surgeries = c.get_surgery_list()
if not surgeries:
    print("[-] No surgeries.")
    exit()

# Test Q050 for the first patient
s = surgeries[0]
ordseq = s['ORDSEQ']
hhistnum = s['HHISTNUM']
print(f"Testing Q050 for {ordseq} / {hhistnum}")

charging = c.get_anesthesia_charging_data(ordseq, hhistnum)
if charging:
    print(f"Tables: {list(charging.keys())}")
    opdordm = charging.get('OPDORDM', [])
    print(f"\nAll OPDORDM items ({len(opdordm)}):")
    mat_551 = []
    for item in opdordm:
        code = item.get('PFKEY', '')
        name = item.get('PFNM', '')
        dose = item.get('DOSE', '')
        prefix = "***551***" if code.startswith('551') else ""
        print(f"  {code:<14} | {name:<45} | qty={dose} {prefix}")
        if code.startswith('551'):
            mat_551.append(item)
    
    print(f"\n551-prefix materials: {len(mat_551)}")
    for m in mat_551:
        print(f"  {m.get('PFKEY','')} | {m.get('PFNM','')}")
    
    # Also check OCCURENCS
    occ = charging.get('OCCURENCS', [])
    print(f"\nOCCURENCS ({len(occ)}):")
    for o in occ[:10]:
        print(f"  {o.get('PFCODE','')} | {o.get('ORDPROCED','')} | qty={o.get('OCQNTY','')}")
    
    # ORRANER
    ane = charging.get('ORRANER', [])
    print(f"\nORRANER ({len(ane)}):")
    if ane:
        print(json.dumps(ane[0], indent=2, ensure_ascii=False))
else:
    print("No charging data.")
