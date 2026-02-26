import zlib
import re

def inspect_q050_payload():
    try:
        with open("q050_payload_0.bin", "rb") as f:
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
            
        # Check for specific patient ID format seen in surgery list
        print("\n--- Potential Values ---")
        # Matches found in previous steps for reference
        # ORDSEQ: A75176778OR0001
        # HHISTNUM: 003356125A
        
        ids = re.findall(r'[A-Z0-9]{8,}', text)
        for i in ids:
            print(i)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_q050_payload()
