import zlib
import re

def analyze_body(filename):
    print(f"\n{'='*60}")
    print(f" FILE: {filename}")
    print(f"{'='*60}")
    with open(filename, "rb") as f:
        data = f.read()
    
    decompressed = None
    for head in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
        start = data.find(head)
        if start != -1:
            try:
                decompressed = zlib.decompress(data[start:])
                print(f"[SUCCESS] Decompressed using {head.hex()} at offset {start}")
                break
            except:
                continue
    
    if not decompressed:
        decompressed = data
        
    text = decompressed.decode('ascii', errors='ignore')
    
    # 1. Look for Facade/Method
    facade_match = re.search(r'([A-Za-z0-9_]*Facade)', text)
    print(f"Facade: {facade_match.group(1) if facade_match else 'Unknown'}")
    
    # 2. Look for Methods (often follows a string like mHIS or similar)
    methods = re.findall(r'mHIS\.[A-Za-z\.]*\.([A-Za-z0-9_]*)', text)
    print(f"Inferred Methods: {set(methods)}")
    
    # 3. Look for Parameters
    params = re.findall(rb'([A-Z0-9_]{4,})\x00', decompressed)
    print(f"Found Params: {set([p.decode() for p in params])}")
    
    # 4. Look for Patient IDs
    ids = re.findall(r'00\d{7}[A-Z]', text)
    print(f"Patient IDs: {set(ids)}")

analyze_body("body_1361.bin")
analyze_body("body_1445.bin")
analyze_body("body_1093.bin")
analyze_body("body_2026.bin")
