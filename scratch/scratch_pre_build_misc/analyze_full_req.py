import zlib
import re

def inspect_full_req(filename):
    print(f"--- Inspecting {filename} ---")
    with open(filename, "rb") as f:
        data = f.read()
    
    # Body might be zlib compressed
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
    
    # Look for Parameter names and values
    # In HIS datasets, parameters are often serialized as strings
    # Pattern: [ParamName] followed by its type and value
    
    print("\n--- Potential Parameters ---")
    # Find all sequences that look like parameter names (capital letters + numbers)
    params = re.findall(rb'([A-Z0-9_]{3,})\x00', decompressed)
    for p in set(params):
        p_str = p.decode()
        # Find the value following it
        # This is a bit dirty but let's see
        idx = decompressed.find(p + b"\x00")
        snippet = decompressed[idx:idx+200]
        print(f"Param: {p_str}")
        print(f"  Snippet: {snippet.decode('ascii', errors='ignore')[:100]}")

    print("\n--- HHISTNUM / ORDSEQ strings ---")
    ids = re.findall(r'00\d{7}[A-Z]|A\d{9}OR\d{4}', text)
    for i in set(ids):
        print(f"Found ID/ORDSEQ: {i}")

inspect_full_req("full_req_2026.bin")
