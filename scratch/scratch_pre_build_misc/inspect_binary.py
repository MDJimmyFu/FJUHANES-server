import zlib
import struct

def inspect_binary():
    try:
        with open("c250_response.bin", "rb") as f:
            data = f.read()
        
        decompressed = zlib.decompress(data)
        print(f"Decompressed {len(decompressed)} bytes.")
        
        # Print first 64 bytes hex
        print("Header (Hex):")
        print(decompressed[:64].hex())
        
        # .NET Binary Formatter usually starts with a header.
        # Strings are length-prefixed.
        # Scan for length-prefixed strings.
        # Length is usually a 7-bit encoded int (variable length) or just int32?
        # In .NET Remoting, it's often:
        # [0x06] [StringObjectID] [Length (Variable)] [UTF-8 Bytes]
        # or simplified: [0x... string type] [Length] [Bytes]
        
        print("\nScanning for string-like chunks...")
        
        # Heuristic: Find a sequence of printable bytes > 4 chars
        import re
        # This regex looks for UTF-8 sequences.
        # Traditional Chinese in UTF-8 is E4-E9 prefix.
        
        # Let's try to just find "HNAMEC" and see what's around it.
        needle = b"<HNAMEC>"
        idx = decompressed.find(needle)
        if idx != -1:
            print(f"Found {needle} at {idx}")
            # Look at bytes around it
            context = decompressed[idx : idx + 30]
            print(f"Context (Hex): {context.hex()}")
            try:
                print(f"Context (UTF-8): {context.decode('utf-8')}")
            except:
                print("Context (UTF-8 decode failed)")
                
            # Look for the VALUE of HNAMEC.
            # <HNAMEC>Name</HNAMEC>
            # Find the closing tag
            close_tag = b"</HNAMEC>"
            end_idx = decompressed.find(close_tag, idx)
            if end_idx != -1:
                value_bytes = decompressed[idx + len(needle) : end_idx]
                print(f"Value Bytes: {value_bytes.hex()}")
                
                for enc in ['utf-8', 'big5', 'cp950']:
                    try:
                        print(f"Decode {enc}: {value_bytes.decode(enc)}")
                    except:
                        print(f"Decode {enc}: Failed")
        else:
            print("HNAMEC tag not found in binary.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_binary()
