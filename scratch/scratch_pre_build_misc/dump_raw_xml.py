from his_client_final import HISClient
import zlib, requests, os, sys, re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
hhistnum = "003086248H"
ordseq = "E46807442OR0019"
opdate = "20260218"

print(f"[*] Fetching raw XML for {hhistnum}...")

with open(c.c430_template, "rb") as f:
    compressed_template = f.read()
decompressed = zlib.decompress(compressed_template)

# Template values
template_hhistnum = b"003356125A"
template_ordseq = b"A75176778OR0001"
template_opdate = b"20260212"

patched = decompressed.replace(template_hhistnum, hhistnum.encode('ascii'))
patched = patched.replace(template_ordseq, ordseq.encode('ascii'))
patched = patched.replace(template_opdate, opdate.encode('ascii'))

final_payload = zlib.compress(patched)
response = requests.post(f"{c.base_url}/HISOrmC430Facade", data=final_payload, headers=c.headers)
raw_text = zlib.decompress(response.content).decode('utf-8', errors='replace')

if "F223822119" in raw_text:
    print("[!] SUCCESS: Found F223822119 in raw XML!")
    import re
    # Find the tag containing it
    match = re.search(r'<(\w+)>F223822119</\1>', raw_text)
    if match:
        print(f"Tag: {match.group(1)}")
    else:
        # Check if it's in a larger block
        snippet = re.search(r'.{0,50}F223822119.{0,50}', raw_text)
        if snippet:
            print(f"Context: {snippet.group(0)}")
else:
    print("[-] F223822119 not found in raw XML.")

# Also check other tables returned
print("\nTables found in XML:")
tables = re.findall(r'<(\w+)\s+diffgr:id', raw_text)
print(set(tables))
