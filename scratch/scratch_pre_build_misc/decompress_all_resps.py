import zlib
import re
import glob
import os

def decompress_resp(filename):
    print(f"\n--- Decompressing {filename} ---")
    try:
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
                # Show first 500 chars to identify table
                print(f"Content Start: {text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

files = glob.glob("resp_*.bin")
for f in files:
    decompress_resp(f)
