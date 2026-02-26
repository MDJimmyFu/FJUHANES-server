import requests
import zlib
import re

headers = {
    "Content-Type": "application/octet-stream",
    "X-Compress": "yes",
    "User-Agent": "Mozilla/4.0+(compatible; MSIE 6.0; Windows 6.2.9200.0; MS .NET Remoting; MS .NET CLR 2.0.50727.9164 )",
    "Expect": "100-continue"
}

base_url = "http://10.10.246.90:8800"

def test_mixed_template(hhistnum, ordseq):
    # 1. Activate using PCAP binary
    print(f"[*] Activating using body_1318.bin...")
    with open("body_1318.bin", "rb") as f:
        c250_body = zlib.decompress(f.read())
    
    # Already for 003617083J
    requests.post(f"{base_url}/HISOrmC250Facade", data=zlib.compress(c250_body), headers=headers)

    # 2. Query using MY template (c430_payload_0.bin)
    print(f"[*] Querying using c430_payload_0.bin...")
    with open("c430_payload_0.bin", "rb") as f:
        c430_comp = f.read()
    c430_body = zlib.decompress(c430_comp)
    
    # Needs patching
    t_h = b"003356125A"
    t_o = b"A75176778OR0001"
    t_d = b"20260212"
    patched = c430_body.replace(t_h, hhistnum.encode('ascii'))
    patched = patched.replace(t_o, ordseq.encode('ascii'))
    patched = patched.replace(t_d, b"20260218")
    
    resp = requests.post(f"{base_url}/HISOrmC430Facade", data=zlib.compress(patched), headers=headers)
    text = zlib.decompress(resp.content).decode('ascii', errors='replace')
    
    if "<INSPECTION" in text:
        print("[SUCCESS] Found <INSPECTION> with mixed templates!")
    else:
        print("[-] Laboratory data missing with mixed templates.")

if __name__ == "__main__":
    test_mixed_template("003617083J", "A75176986OR0041")
