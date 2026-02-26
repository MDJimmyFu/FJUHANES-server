def inspect_bin(path):
    with open(path, "rb") as f:
        data = f.read()
    print(f"Path: {path}")
    print(f"Size: {len(data)}")
    print(f"First 100 bytes (hex): {data[:100].hex()}")
    
    # Try decompressing
    import zlib
    try:
        dec = zlib.decompress(data)
        print(f"Decompressed size: {len(dec)}")
        print(f"Decompressed first 500 bytes: {dec[:500]}")
        # Search for known template ID from his_client_final.py
        # template_hhistnum = b"003356125A" (used in C430)
        # Template date from get_surgery_list: b"20260211"
        if b"003356125A" in dec: print("Found 003356125A")
        if b"20260211" in dec: print("Found 20260211")
    except:
        print("Not a zlib stream or decompress failed.")

inspect_bin("c250_payload_0.bin")
inspect_bin("c430_payload_0.bin")
