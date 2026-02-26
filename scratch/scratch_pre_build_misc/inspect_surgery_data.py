from his_client_final import HISClient
import datetime
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
date_str = datetime.datetime.now().strftime("%Y%m%d")
print(f"[*] Fetching surgery list for {date_str}...")

data = c.get_surgery_list(date_str)

if data:
    print(f"[+] Found {len(data)} surgeries.")
    # Print keys of the first few items to find urgency field
    for i, item in enumerate(data[:5]):
        print(f"\n--- Item {i+1} ---")
        for k, v in item.items():
            if v: print(f"{k}: {v}")
            
    # Check specifically for urgency candidates
    urgency_keys = ['EMG', 'URGENCY', 'CLASS', 'TYPE', 'CODE', 'LEVEL']
    print("\n[*] Checking for urgency fields...")
    for item in data:
        for k, v in item.items():
            if any(uk in k.upper() for uk in urgency_keys):
                print(f"  {k}: {v}")
                
        # Check for status '完成'
        if '完成' in str(item.get('STATUS', '')):
             print(f"  [!] Found completed surgery: {item.get('STATUS')}")

else:
    print("[-] No surgeries found today.")
