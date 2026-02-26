import zlib
import glob
import os

files = glob.glob("*payload*.bin")

for f in files:
    print(f"\n--- {f} ---")
    try:
        with open(f, "rb") as bf:
            data = bf.read()
        
        # Binary data often has some header before zlib
        # Try to find the start of zlib (78 9C or 78 01)
        start = data.find(b"\x78\x9c")
        if start == -1:
            start = data.find(b"\x78\x01")
            
        if start != -1:
            decompressed = zlib.decompress(data[start:])
            # Try to decode as ascii/utf-8 with ignore
            text = decompressed.decode('ascii', errors='ignore')
            # Look for interesting strings
            # If it's a HISExmFacade, it might have a SQL query
            print(text[:2000]) # Print first 2k chars
        else:
            print("[-] No zlib signature found")
            print(data[:500]) # Print raw start
    except Exception as e:
        print(f"[-] Error: {e}")
