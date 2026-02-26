from his_client_final import HISClient
import json

c = HISClient()
surg = c.get_surgery_list()
if surg:
    first = surg[0]
    print(json.dumps(first, indent=4, ensure_ascii=False))
    print(f"\nKeys: {list(first.keys())}")
else:
    print("No surgery found")
