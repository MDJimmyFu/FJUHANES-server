import zlib
import glob
import os

files = glob.glob("*payload*.bin")

for f in files:
    print(f"\n{'#'*40}")
    print(f" FILE: {f}")
    print(f"{'#'*40}")
    try:
        with open(f, "rb") as bf:
            data = bf.read()
        
        # Try different zlib headers
        # \x78\x01 (No/Low compression)
        # \x78\x9c (Default compression)
        # \x78\xda (Best compression)
        found = False
        for head in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
            start = data.find(head)
            if start != -1:
                try:
                    decompressed = zlib.decompress(data[start:])
                    text = decompressed.decode('ascii', errors='ignore')
                    print(f"[SUCCESS] Decompressed using {head.hex()} at offset {start}")
                    print(text[:3000]) # Print more to be sure
                    found = True
                    break
                except:
                    continue
        
        if not found:
            print("[-] FAILED to decompress with standard zlib headers.")
            # Print raw snippet to see what's there
            print(f"Raw Snippet: {data[:200].hex()}")
            print(f"Stringified Snippet: {data[:200].decode('ascii', errors='ignore')}")

    except Exception as e:
        print(f"[-] Error parsing {f}: {e}")
