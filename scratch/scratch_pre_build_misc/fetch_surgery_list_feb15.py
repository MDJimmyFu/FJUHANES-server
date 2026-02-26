from his_client_final import HISClient

client = HISClient()

hhistnum = '003617083J'

# The pre-op assessment was done on 2026-02-15
# Let's get the surgery list for 2026-02-15 and find the ORDSEQ for this patient
print("Fetching surgery list for 2026-02-15...")
surgeries = client.get_surgery_list('20260215')

if surgeries:
    print(f"[+] Got {len(surgeries)} surgeries")
    for s in surgeries:
        if s.get('HHISTNUM') == hhistnum:
            print(f"\n[+] Found patient {hhistnum} in 2026-02-15 surgery list!")
            for k, v in s.items():
                print(f"  {k}: {v}")
else:
    print("[-] No surgeries returned for 2026-02-15.")

# Also try 2026-02-16 and 2026-02-17
for date in ['20260216', '20260217']:
    print(f"\nFetching surgery list for {date}...")
    surgeries = client.get_surgery_list(date)
    if surgeries:
        for s in surgeries:
            if s.get('HHISTNUM') == hhistnum:
                print(f"[+] Found patient {hhistnum} in {date} surgery list!")
                for k, v in s.items():
                    print(f"  {k}: {v}")
    else:
        print(f"[-] No surgeries returned for {date}.")
