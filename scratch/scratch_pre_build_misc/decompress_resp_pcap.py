import zlib
import re

def decompress_resp(filename):
    print(f"\n--- Decompressing {filename} ---")
    with open(filename, "rb") as f:
        data = f.read()
    
    # Skip headers
    start = data.find(b"\r\n\r\n")
    if start != -1:
        data = data[start+4:]
        
    decompressed = None
    for head in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
        offset = data.find(head)
        if offset != -1:
            try:
                decompressed = zlib.decompress(data[offset:])
                print(f"[SUCCESS] Decompressed at offset {offset}")
                break
            except:
                continue
    
    if decompressed:
        text = decompressed.decode('utf-8', errors='replace')
        # Check for INSPECTION
        if "<INSPECTION" in text:
            print("[!!!!] FOUND <INSPECTION> in this response!")
            # Save it
            with open(filename.replace(".bin", ".xml"), "w", encoding="utf-8") as out:
                out.write(text)
        else:
            print("[-] No <INSPECTION> found.")
            # Print tags found
            tags = set(re.findall(r'<(\w+)\s+diffgr:id', text))
            print(f"Tags found: {tags}")

decompress_resp("resp_1479_raw.bin")
decompress_resp("resp_1445_raw.bin")
decompress_resp("resp_1500_raw.bin")
