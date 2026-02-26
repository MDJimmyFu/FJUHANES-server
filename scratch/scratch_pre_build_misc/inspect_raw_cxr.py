from his_client_final import HISClient
import json, sys, zlib, re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target_patient = "003509917D"
target_ordseq = "A75177038OR0007"
target_date = "20260218"

print(f"[*] Fetching raw C430 for {target_patient}...")
c.activate_patient(target_patient, target_ordseq)

with open(c.c430_template, "rb") as f:
    compressed_template = f.read()
decompressed = zlib.decompress(compressed_template)
patched_payload = decompressed.replace(b"003162935D", target_patient.encode('ascii'))
patched_payload = patched_payload.replace(b"A75072943OR0001", target_ordseq.encode('ascii'))
patched_payload = patched_payload.replace(b"20260212", target_date.encode('ascii'))
final_payload = zlib.compress(patched_payload)

import requests
response = requests.post(f"{c.base_url}/HISOrmC430Facade", data=final_payload, headers=c.headers)
raw_text = zlib.decompress(response.content).decode('utf-8', errors='replace')

cxr_match = re.search(r'<CXR[^>]*>(.*?)</CXR>', raw_text, re.DOTALL)
if cxr_match:
    print("\n--- Raw CXR Table Row ---")
    row_xml = cxr_match.group(1)
    fields = re.findall(r'<(\w+)>(.*?)</\1>', row_xml)
    for k, v in fields:
        print(f"{k}: {v}")
else:
    print("CXR table not found in raw XML.")

# Look for URL or report links
print("\n[*] Searching for URLs or links...")
urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', raw_text)
for url in urls:
    print(f"  Found URL: {url}")

if 'URL' in raw_text:
    print("Found 'URL' string in raw text!")
    match = re.search(r'<(.*?)>.*?URL.*?</\1>', raw_text, re.DOTALL)
    if match: print(f"Snippet: {match.group(0)}")
