import zlib
import re

def inspect_c430_payload():
    try:
        with open("c430_payload_0.bin", "rb") as f:
            data = f.read()
            
        print(f"Compressed size: {len(data)}")
        
        try:
            decompressed = zlib.decompress(data)
            print(f"Decompressed size: {len(decompressed)}")
        except:
            print("Payload is not zlib compressed? trying raw.")
            decompressed = data

        # Print all strings > 4 chars
        text = decompressed.decode('utf-8', errors='ignore')
        strings = re.findall(r'[A-Za-z0-9\-\.:]{4,}', text)
        
        print("\n--- Strings in Payload ---")
        for s in strings:
            print(s)
            
        # Check for specific patient ID format seen in surgery list (e.g. 003.....C)
        print("\n--- Potential IDs ---")
        ids = re.findall(r'\d{6,}', text)
        for i in ids:
            print(i)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_c430_payload()
