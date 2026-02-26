import zlib
import re

def parse_response():
    try:
        with open("c250_response.bin", "rb") as f:
            data = f.read()
        
        print(f"Read {len(data)} bytes.")
        
        # Try Zlib decompression
        try:
            decompressed = zlib.decompress(data)
            print(f"Decompressed size: {len(decompressed)}")
        except Exception as e:
            print(f"Zlib decompression failed: {e}")
            # It might be raw binary without compression, or have a header
            # .NET Remoting often uses GZip/Deflate, or custom.
            # But 'x\xda' is standard zlib header.
            return

        # Save decompressed
        with open("c250_response_decompressed.bin", "wb") as f:
            f.write(decompressed)
            
        decompressed_text = decompressed.decode('utf-8', errors='ignore')
        print("Decompressed Content Preview:")
        print(decompressed_text[:1000])
        
        # Look for surgery info
        if "ORDOP" in decompressed_text or "OPSTA" in decompressed_text:
             print("\n[+] Found surgery related keywords!")
        else:
             print("\n[-] No obvious surgery keywords found.")
             
        # It looks like .NET Binary Serialization.
        # Strings are Length Prefixed.
        # Let's try to extract strings more cleanly.
        strings = re.findall(r'[A-Za-z0-9\-\.:\u4e00-\u9fa5]{4,}', decompressed_text)
        print("\nExtracted Strings:")
        for s in strings:
            print(s)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parse_response()
