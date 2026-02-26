from his_client_final import HISClient
import json, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()

# Test the new get_anesthesia_history method
hhistnum = "003363078D"
print(f"=== Testing get_anesthesia_history({hhistnum}) ===")
history = c.get_anesthesia_history(hhistnum)
print(f"\nTotal records: {len(history)}")
for h in history:
    print(f"  ORDSEQ={h.get('ORDSEQ','')} | Method={h.get('ANENM','')} | ASA={h.get('ANEASA','')} | Doctor={h.get('ANEDOCNMC', h.get('PROCNMC',''))} | Start={h.get('ANEBGNDTTM','')}")

# Filter out LA/NI (like the API does)
filtered = [h for h in history if h.get('ANENM', '') not in ('LA', 'NI')]
print(f"\nFiltered (no LA/NI): {len(filtered)}")

# For each filtered record, try Q050
for h in filtered:
    ordseq = h.get('ORDSEQ', '')
    print(f"\n--- Q050 for {ordseq} ---")
    charging = c.get_anesthesia_charging_data(ordseq, hhistnum)
    if charging:
        print(f"Tables: {list(charging.keys())}")
        # 551-prefix materials
        opdordm = charging.get('OPDORDM', [])
        mat551 = [i for i in opdordm if i.get('PFKEY', '').startswith('551')]
        print(f"OPDORDM total: {len(opdordm)}, 551-prefix: {len(mat551)}")
        for m in mat551:
            print(f"  {m.get('PFKEY','')} | {m.get('PFNM','')} | qty={m.get('DOSE','')}")
        
        # All items
        print(f"All OPDORDM:")
        for i in opdordm:
            pfx = " ***551***" if i.get('PFKEY','').startswith('551') else ""
            print(f"  {i.get('PFKEY',''):<14} | {i.get('PFNM',''):<40}{pfx}")
    else:
        print("  No Q050 data")
