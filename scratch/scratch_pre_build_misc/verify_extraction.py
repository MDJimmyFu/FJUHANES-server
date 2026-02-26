import requests
import re
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

caseno = "46807673"
base_url = "http://10.10.242.59/consult_query/"
list_url = f"{base_url}consult_form.php?HCASENO={caseno}"

print(f"[*] Testing extraction from: {list_url}")
try:
    resp = requests.get(list_url, timeout=10)
    if resp.status_code == 200:
        html = resp.text
        links = re.findall(r"consult_form_view\.php\?[^']+", html)
        print(f"[+] Found {len(links)} consultation links.")
        for link in links:
            print(f"  - {link}")
            
        # Test fetching the first link
        if links:
            full_link = f"{base_url}{links[0]}"
            print(f"[*] Fetching detail: {full_link}")
            detail_resp = requests.get(full_link, timeout=10)
            if detail_resp.status_code == 200:
                print(f"[+] Detail content length: {len(detail_resp.text)}")
                print(f"[+] Preview:\n{detail_resp.text[:200]}...")
            else:
                print(f"[-] Detail fetch failed: {detail_resp.status_code}")
    else:
        print(f"[-] List fetch failed: {resp.status_code}")
except Exception as e:
    print(f"[-] Error: {e}")
