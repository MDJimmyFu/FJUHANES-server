import requests
import json

url = "http://127.0.0.1:5000/api/details"
payload = {
    "hhistnum": "003617083J",
    "ordseq": "A75176986OR0041"
}

headers = {
    "Content-Type": "application/json"
}

print(f"[*] Testing API with: {payload}")
response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("[+] API Success!")
    print("\n--- Lab Data Found ---")
    lab_data = data.get("lab_data", {})
    for k, v in lab_data.items():
        print(f"  {k:10}: {v}")
else:
    print(f"[-] API Error {response.status_code}: {response.text}")
