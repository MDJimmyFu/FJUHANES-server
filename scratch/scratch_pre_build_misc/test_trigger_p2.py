import requests
import zlib
import re

# Same headers as PCAP
headers = {
    "Content-Type": "application/octet-stream",
    "X-Compress": "yes",
    "User-Agent": "Mozilla/4.0+(compatible; MSIE 6.0; Windows 6.2.9200.0; MS .NET Remoting; MS .NET CLR 2.0.50727.9164 )",
    "Expect": "100-continue"
}

base_url = "http://10.10.246.90:8800"

def test_sequence(hhistnum, ordseq):
    # 1. Call C250 for patient (Mimic Request 1318)
    print(f"[*] Calling C250 for {hhistnum} / {ordseq}...")
    with open("c250_payload_1.bin", "rb") as f:
        c250_template = zlib.decompress(f.read())
    
    # Patch C250 template with patient info
    # Template has some other patient. Let's find them.
    # In body_1318 strings: 15d9: 003509917D, 16a6: A75177038OR0007
    # Actually I'll use body_1318.bin as template if possible.
    
    with open("body_1318.bin", "rb") as f:
        c250_body = zlib.decompress(f.read())
    
    # Already has 003509917D / A75177038OR0007
    resp_c250 = requests.post(f"{base_url}/HISOrmC250Facade", data=zlib.compress(c250_body), headers=headers)
    print(f"[C250] Status: {resp_c250.status_code}")

    # 2. Call C430 for patient (Mimic Request 1445)
    print(f"[*] Calling C430 for {hhistnum} / {ordseq}...")
    with open("body_1445.bin", "rb") as f:
        c430_body = zlib.decompress(f.read())
    
    resp_c430 = requests.post(f"{base_url}/HISOrmC430Facade", data=zlib.compress(c430_body), headers=headers)
    print(f"[C430] Status: {resp_c430.status_code}")
    
    if resp_c430.status_code == 200:
        text = zlib.decompress(resp_c430.content).decode('ascii', errors='replace')
        if "<INSPECTION" in text:
            print("[SUCCESS] FOUND <INSPECTION> in live response!")
        else:
            print("[-] No <INSPECTION> found in live response.")
            # Show tables found
            tables = re.findall(r'<(\w+)\s+diffgr:id', text)
            print(f"Tables present: {set(tables)}")

if __name__ == "__main__":
    test_sequence("003509917D", "A75177038OR0007")
