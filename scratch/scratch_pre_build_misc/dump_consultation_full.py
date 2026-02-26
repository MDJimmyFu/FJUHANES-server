import requests
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

caseno = "46807673"
url = f"http://10.10.242.59/consult_query/consult_form.php?HCASENO={caseno}"

print(f"[*] Fetching full content from: {url}")
try:
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        print(resp.text)
    else:
        print(f"[-] Failed: {resp.status_code}")
except Exception as e:
    print(f"[-] Error: {e}")
