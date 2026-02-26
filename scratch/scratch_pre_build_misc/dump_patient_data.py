from his_client_final import HISClient
import json
import datetime
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

client = HISClient()
target_hhistnums = ['003617083J', '003509917D']
param_map = {} # Store ORDSEQ for each if found

print(f"[*] targets: {target_hhistnums}")

# 1. Fetch Surgery List to get ORDSEQ (using likely dates)
# The pcap had data from Feb 18 (20260218). Let's check a range just in case.
# But we really need the one that corresponds to the "current" active surgery.
check_dates = ['20260218'] 

# Hardcoded Fallback derived from PCAP analysis
# 003617083J -> A75176986OR0041 (Found in 78da_8.xml)
# 003509917D -> A75177038OR0007 (Derived from 78da_5.xml context or similar? Wait, let's re-verify)

# In the previous grep for 003509917D, we saw PAT_ADM_DRMEMO in 78da_8.xml with HCASENO 75177038.
# And in 78da_5.xml we saw "A75177038OR0007" associated with HCASENO 75177038?
# Let's assume A75177038OR0007 is correct based on the pattern (75177038 + OR + seq).
# Actually, the grep output for 78da_5.xml showed: <ORDSEQ>A75176986OR0041</ORDSEQ> which is for 003617083J.
# But for 003509917D?
# In 78da_8.xml grep output (Step 2303):
# <ORRANER ...><ORDSEQ>A75177038OR0007</ORDSEQ><HCASENO>75177038</HCASENO>...
# <PAT_ADM_DRMEMO ...><HHISNUM>003509917D</HHISNUM><HCASENO>75177038</HCASENO>
# So 003509917D maps to A75177038OR0007.

param_map = {
    '003617083J': 'A75176986OR0041',
    '003509917D': 'A75177038OR0007' 
}

print(f"[*] Resolved ORDSEQs: {param_map}")

# 2. Fetch Detailed Data for targets
for pat in target_hhistnums:
    print(f"\n{'='*60}")
    print(f" DATA DUMP FOR PATIENT: {pat}")
    print(f"{'='*60}")
    
    ordseq = param_map.get(pat)
    if not ordseq:
        print("[-] No ORDSEQ found. Cannot fetch detailed C430/Q050 data.")
        # We can still try EXM / Patient Info?
        # But let's mainly focus on C430 structure first if possible.
        # Actually, for the purpose of "Available Data", maybe we can try to find ANY ordseq via SQL?
        # Only if we implement that. For now, rely on list.
        continue

    # A. Pre-Anesthesia (C430)
    print(f"\n--- 1. Pre-Anesthesia (HISOrmC430Facade) ---")
    pre = client.get_pre_anesthesia_data(ordseq, pat)
    if pre:
        print(f"Available Tables: {list(pre.keys())}")
        for table, rows in pre.items():
            print(f"\n  [{table}] ({len(rows)} rows)")
            # Print first row keys and values to see what we have
            if rows:
                keys = rows[0].keys()
                print(f"  Keys: {', '.join(keys)}")
                for i, r in enumerate(rows):
                    print(f"    Row {i}: {r}")
    else:
        print("[-] No Data Returned")

    # B. Charging (Q050)
    print(f"\n--- 2. Charging (HISOrmC250Facade Q050) ---")
    chg = client.get_anesthesia_charging_data(ordseq, pat)
    if chg:
        print(f"Available Tables: {list(chg.keys())}")
        for table, rows in chg.items():
            print(f"\n  [{table}] ({len(rows)} rows)")
            if rows:
                keys = rows[0].keys()
                print(f"  Keys: {', '.join(keys)}")
                for i, r in enumerate(rows):
                    print(f"    Row {i}: {r}")

    # C. Vitals (EXM)
    print(f"\n--- 3. Vitals via SQL (HISExmFacade) ---")
    vitals = client.get_vitals_from_exm(pat, ordseq)
    if vitals:
        print(f"Found Vitals: {vitals}")
    else:
        print("[-] No Vitals found")
        
    print(f"\n[End Dump for {pat}]")
