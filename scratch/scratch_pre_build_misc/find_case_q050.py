from his_client_final import HISClient
import sys
import re

def find_case(target_caseno):
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    client = HISClient()
    print(f"[*] Searching surgery list for Case No: {target_caseno}...")
    
    surgeries = client.get_surgery_list()
    
    found = None
    if surgeries:
        for s in surgeries:
            # Check if CASENO is in ORDSEQ (e.g. A75176797OR...)
            # or if we can find it in the raw row if we parsed it? 
            # Current parsed keys: room, bed, doctor, patient, procedure, ordseq, hhistnum
            
            if target_caseno in s['ordseq']:
                print(f"[+] Found match in ORDSEQ: {s['ordseq']}")
                found = s
                break
    
    if not found:
        print("[-] Not found in today's list. Checking yesterday (20260211)...")
        surgeries = client.get_surgery_list("20260211")
        if surgeries:
            for s in surgeries:
                if target_caseno in s['ordseq']:
                    print(f"[+] Found match in ORDSEQ: {s['ordseq']}")
                    found = s
                    break
                
            # Also check HCASENO if we parsed it? We didn't parse HCASENO in surgery list yet.
            # But usually ORDSEQ contains it.
            
    if found:
        print(f"[+] Found Patient: {found['patient']}")
        print(f"    ORDSEQ: {found['ordseq']}")
        print(f"    HHISTNUM: {found['hhistnum']}")
        
        print("\n[*] Fetching Q050 Data...")
        charging = client.get_anesthesia_charging_data(found['ordseq'], found['hhistnum'])
        
        if charging:
             print(f"[+] Retrieved {len(charging)} tables of CHARGING data.")
             
             # 1. Anesthesia Info
             if 'ORRANER' in charging and charging['ORRANER']:
                 aner = charging['ORRANER'][0]
                 print(f"\n--- Anesthesia Info ---")
                 start = aner.get('ANEBGNDTTM')
                 end = aner.get('ANEENDDTTM')
                 if start and end: 
                     print(f"  Duration: {start} -> {end}")
                 print(f"  Anesthesiologist: {aner.get('ANEDOCNMC', aner.get('PROCNMC', 'N/A'))}")
                 print(f"  Supervisor: {aner.get('ANESUPVNMC', 'N/A')}")

             # 2. Charging/Procedures
             if 'OPDORDM' in charging and charging['OPDORDM']:
                 materials = []
                 procedures = []
                 for item in charging['OPDORDM']:
                     code = item.get('PFKEY', '')
                     if code.startswith('M'): materials.append(item)
                     else: procedures.append(item)
                 
                 if procedures:
                     print(f"\n--- Procedures & Billing (OPDORDM) ---")
                     for item in procedures:
                         print(f"{item.get('PFKEY',''):<12} | {item.get('PFNM',''):<40} | {item.get('DOSE','')}")

             if 'COMMON_ORDER' in charging and charging['COMMON_ORDER']:
                 print(f"\n--- Anesthesia Items (COMMON_ORDER) ---")
                 for item in charging['COMMON_ORDER']:
                     code = item.get('PFCODE', '')
                     name = item.get('ORDPROCED', '')
                     print(f"{code:<12} | {name:<40}")

             if 'OCCURENCS' in charging and charging['OCCURENCS']:
                 print(f"\n--- Occurrences (OCCURENCS) ---")
                 for item in charging['OCCURENCS']:
                     code = item.get('PFCODE', '')
                     name = item.get('ORDPROCED', '')
                     qty = item.get('OCQNTY', '')
                     print(f"{code:<12} | {name:<40} | {qty}")

             if 'OPDORDM' in charging and charging['OPDORDM']:
                 if materials:
                     print(f"\n--- Materials (材料費) ---")
                     for item in materials:
                         print(f"{item.get('PFKEY',''):<12} | {item.get('PFNM',''):<40} | {item.get('DOSE','')}")
        else:
             print("[-] No charging data found.")

    else:
        print("[-] Case not found in today's surgery list.")

if __name__ == "__main__":
    find_case("75176750")
