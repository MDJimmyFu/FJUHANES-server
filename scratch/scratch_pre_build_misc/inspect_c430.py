from his_client_final import HISClient
import json

client = HISClient()
# Use the found patient credentials
ordseq = 'A75176986OR0041'
hhistnum = '003617083J'

print(f"Fetching C430 for {ordseq}...")
data = client.get_pre_anesthesia_data(ordseq, hhistnum)

if not data:
    print("No data found.")
    exit()

print(f"All Keys in Data: {list(data.keys())}")

print("\n--- PAT_ADM_DRMEMO (C430) ---")
print(json.dumps(data.get('PAT_ADM_DRMEMO', []), indent=2, ensure_ascii=False))

print("\n[*] Fetching anesthesia charging data (Q050)...")
charging = client.get_anesthesia_charging_data(ordseq, hhistnum)
if charging:
    print(f"Q050 Keys: {list(charging.keys())}")
    print("\n--- PAT_ADM_CASE (Q050) ---")
    print(json.dumps(charging.get('PAT_ADM_CASE', []), indent=2, ensure_ascii=False))
else:
    print("No Q050 data found.")

print("\n[*] Fetching Surgery List Entry (C250) for Debugging...")
surgery_list = client.get_surgery_list()
for item in surgery_list:
    if item.get('HHISTNUM') == hhistnum or item.get('HHISTNUM') == hhistnum:
        print("\n--- C250 Entry ---")
        print(json.dumps(item, indent=2, ensure_ascii=False))
        break

print("\n--- VITALSIGN_BTVALUE (Temp) ---")
print(json.dumps(data.get('VITALSIGN_BTVALUE', [])[:1], indent=2, ensure_ascii=False))

print("\n--- VITALSIGN_PULSEVALUE (Heart Rate) ---")
print(json.dumps(data.get('VITALSIGN_PULSEVALUE', [])[:1], indent=2, ensure_ascii=False))

print("\n--- VITALSIGN_RESPVALUE (Respiratory) ---")
print(json.dumps(data.get('VITALSIGN_RESPVALUE', [])[:1], indent=2, ensure_ascii=False))

print("\n--- VITALSIGN_SBPDBPVALUE (BP) ---")
print(json.dumps(data.get('VITALSIGN_SBPDBPVALUE', [])[:1], indent=2, ensure_ascii=False))

print("\n--- INSPECTION (Lab Data) ---")
print(json.dumps(data.get('INSPECTION', [])[:3], indent=2, ensure_ascii=False))

print("\n--- OPOHOME_PAT_MARKS ---")
print(json.dumps(data.get('OPOHOME_PAT_MARKS', [])[:1], indent=2, ensure_ascii=False))
