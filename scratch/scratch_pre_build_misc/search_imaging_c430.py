from his_client_final import HISClient
import json, sys, zlib, re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
target_patient = "003189572E"
target_ordseq = "A75177003OR0001"
target_date = "20260216"

print(f"[*] Fetching raw C430 data for {target_patient}...")
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

print(f"[*] Raw XML Size: {len(raw_text)}")

# Check for table names
tables = set(re.findall(r'<(\w+)\s+diffgr:id', raw_text))
print(f"[*] Tables found: {tables}")

# Print CXR data
if 'CXR' in tables:
    print("\n--- CXR Data ---")
    cxr_rows = re.findall(r'<CXR[^>]*>(.*?)</CXR>', raw_text, re.DOTALL)
    for row in cxr_rows:
        print(row.strip())

# Search for EKG
print("\n[*] Searching for 'EKG' or 'ECG'...")
if 'EKG' in raw_text or 'ECG' in raw_text:
    print("Found 'EKG' or 'ECG' in raw text!")
    # Find matching tables or tags
    ekg_match = re.search(r'<(.*?)>.*?EKG.*?</\1>', raw_text, re.IGNORECASE | re.DOTALL)
    if ekg_match:
        print(f"Snippet: {ekg_match.group(0)}")
else:
    print("Not found in raw text.")

# Search for REPORT
print("\n[*] Searching for 'REPORT' or 'IMG'...")
for word in ['REPORT', 'IMG', '影像', '放射']:
    if word in raw_text:
        print(f"Found word: {word}")
        # Find context
        match = re.search(f'<(.*?)>.*?{word}.*?</\\1>', raw_text, re.IGNORECASE | re.DOTALL)
        if match:
            print(f"Snippet: {match.group(0)}")

# Print PAT_ADM_DRMEMO labels
print("\n[*] Checking PAT_ADM_DRMEMO Labels:")
labels = re.findall(r'<LABEL>(.*?)</LABEL>', raw_text)
for l in labels:
    print(f"  - {l}")
