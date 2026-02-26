from his_client_final import HISClient
import json, sys, datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
today = datetime.datetime.now().strftime("%Y%m%d")
print(f"[*] Fetching surgery list for {today}...")
surgeries = c.get_surgery_list(today)

if surgeries:
    print(f"[+] Found {len(surgeries)} surgeries.")
    all_table_names = set()
    for s in surgeries[:10]: # Check first 10
        hhistnum = s.get('HHISTNUM')
        ordseq = s.get('ORDSEQ')
        if hhistnum and ordseq:
            print(f"  [*] Checking C430 for {hhistnum} / {ordseq}...")
            data = c.get_pre_anesthesia_data(ordseq, hhistnum, opdate=today)
            if data:
                all_table_names.update(data.keys())
    
    print(f"\n[!] All Table Names found in C430 across 10 patients:")
    print(sorted(list(all_table_names)))
else:
    print("[-] No surgeries found for today.")
