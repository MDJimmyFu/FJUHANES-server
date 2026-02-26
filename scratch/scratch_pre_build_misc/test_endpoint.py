import requests

url = "http://127.0.0.1:5000/api/his/getPatAdmHistoryList"
params = {
    "pHHISNum": "003380272B"
}

try:
    print(f"[*] Testing {url} with params {params}...")
    resp = requests.get(url, params=params)
    print(f"Status Code: {resp.status_code}")
    print(f"Content: {resp.text[:500]}")
except Exception as e:
    print(f"[-] Request failed: {e}")
