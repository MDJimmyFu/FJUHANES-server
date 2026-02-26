from his_client_final import HISClient
import requests
import zlib
import re

client = HISClient()

hhistnum = '003617083J'

# From ORMC430 Memo 2:
# OPID = F129348478 (the pre-op assessment document ID, created 2026-02-15)
# DRMID = 20260218011135
# HCASENO = 75176986
opid = 'F129348478'

# The INSPECTION table was present for patient 003158375C (ORDSEQ: A75176797OR0014)
# For patient 003617083J, the pre-op assessment was done on 2026-02-15 with OPID=F129348478
# Let's try fetching ORMC430 using the OPID as the ORDSEQ parameter

print(f"Trying ORMC430 with OPID {opid} as ORDSEQ...")
data = client.get_pre_anesthesia_data(opid, hhistnum)
if data:
    print(f"[+] Got data! Keys: {list(data.keys())}")
    inspection = data.get('INSPECTION', [])
    print(f"[+] INSPECTION records: {len(inspection)}")
    for rec in inspection[:5]:
        print(f"  {rec}")
else:
    print("[-] No data returned.")

# Also try fetching the raw XML to see what tables are returned
print(f"\nFetching raw ORMC430 XML with OPID as ORDSEQ...")
try:
    with open(client.c430_template, "rb") as f:
        compressed_template = f.read()
    decompressed = zlib.decompress(compressed_template)
    
    template_hhistnum = b"003356125A"
    template_ordseq = b"A75176778OR0001"
    
    patched_payload = decompressed.replace(template_hhistnum, hhistnum.encode('ascii'))
    patched_payload = patched_payload.replace(template_ordseq, opid.encode('ascii'))
    final_payload = zlib.compress(patched_payload)
    
    response = requests.post(f"{client.base_url}/HISOrmC430Facade", data=final_payload, headers=client.headers)
    response.raise_for_status()
    
    raw_text = zlib.decompress(response.content).decode('utf-8', errors='replace')
    
    row_tags = set(re.findall(r'<(\w+)\s+diffgr:id', raw_text))
    print(f"[+] Table tags found: {row_tags}")
    
    with open("ormc430_opid_raw.xml", "w", encoding="utf-8") as f:
        f.write(raw_text)
    print(f"[+] Raw XML written to ormc430_opid_raw.xml ({len(raw_text)} chars)")
    
except Exception as e:
    print(f"[-] Error: {e}")
