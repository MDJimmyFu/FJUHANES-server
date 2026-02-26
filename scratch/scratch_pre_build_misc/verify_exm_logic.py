from his_client_final import HISClient
import json

client = HISClient()
hhistnum = "003617083J"

print(f"Testing get_vitals_from_exm for {hhistnum}...")
vitals = client.get_vitals_from_exm(hhistnum)
print("Result:")
print(json.dumps(vitals, indent=2))
