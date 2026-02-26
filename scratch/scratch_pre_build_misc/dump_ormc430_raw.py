from his_client_final import HISClient
import zlib
import requests
import re

client = HISClient()

ordseq = 'A75176986OR0041'
hhistnum = '003617083J'

print(f"Fetching raw ORMC430 XML for {ordseq} / {hhistnum}...")

try:
    with open(client.c430_template, "rb") as f:
        compressed_template = f.read()
    decompressed = zlib.decompress(compressed_template)
    
    template_hhistnum = b"003356125A"
    template_ordseq = b"A75176778OR0001"
    
    patched_payload = decompressed.replace(template_hhistnum, hhistnum.encode('ascii'))
    patched_payload = patched_payload.replace(template_ordseq, ordseq.encode('ascii'))
    final_payload = zlib.compress(patched_payload)
    
    response = requests.post(f"{client.base_url}/HISOrmC430Facade", data=final_payload, headers=client.headers)
    response.raise_for_status()
    
    raw_text = zlib.decompress(response.content).decode('utf-8', errors='replace')
    
    # Write full raw XML to file
    with open("ormc430_raw.xml", "w", encoding="utf-8") as f:
        f.write(raw_text)
    print(f"[+] Raw XML written to ormc430_raw.xml ({len(raw_text)} chars)")
    
    # Find all table/row tag names
    row_tags = set(re.findall(r'<(\w+)\s+diffgr:id', raw_text))
    print(f"[+] Table tags found: {row_tags}")
    
    # Also find all top-level tags in NewDataSet
    match = re.search(r'<NewDataSet>(.*?)</NewDataSet>', raw_text, re.DOTALL)
    if match:
        inner = match.group(1)
        top_tags = set(re.findall(r'<(\w+)[\s>]', inner))
        print(f"[+] Top-level tags in NewDataSet: {top_tags}")
    
    # Print first 3000 chars of raw XML
    print("\n--- First 3000 chars of raw XML ---")
    print(raw_text[:3000])

except Exception as e:
    print(f"[-] Error: {e}")
    import traceback
    traceback.print_exc()
