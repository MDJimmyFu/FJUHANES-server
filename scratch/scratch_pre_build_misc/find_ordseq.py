from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target = "003600459I"

print(f"[*] Finding ORDSEQ for {target}...")
# I'll search for any surgery list in the last month to find this patient
import datetime
today = datetime.datetime.now()
found = False
for i in range(30):
    d = (today - datetime.timedelta(days=i)).strftime("%Y%m%d")
    slist = c.get_surgery_list(d)
    for s in slist:
        if s.get('HIDNO') == target or s.get('HHISNUM') == target:
            print(f"  [+] Found! Date: {d} ORDSEQ: {s.get('HORDSEQ')}")
            found = True
    if found: break

if not found:
    print("  [-] Not found in recent surgery list. Trying to activate with case 46807110...")
    # Maybe I can just use get_pre_anesthesia_data with a fake/any ordseq if I have HHISNUM?
    # No, usually need a real one.
