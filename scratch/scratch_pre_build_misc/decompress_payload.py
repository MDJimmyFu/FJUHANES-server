import zlib

def decompress_payload():
    try:
        with open("c250_payload_1.bin", "rb") as f:
            data = f.read()
        
        print(f"Read {len(data)} bytes.")
        
        # Try Zlib decompression
        try:
            decompressed = zlib.decompress(data)
            print(f"Decompressed size: {len(decompressed)}")
        except Exception as e:
            print(f"Zlib decompression failed: {e}")
            return

        # Save decompressed
        output_file = "c250_payload_1_decompressed.bin"
        with open(output_file, "wb") as f:
            f.write(decompressed)
            
        print(f"Saved decompressed payload to {output_file}")
        
        # Search for date
        decompressed_text = decompressed.decode('utf-8', errors='ignore')
        if "20260211" in decompressed_text:
             print("Found '20260211' in decompressed payload!")
        else:
             print("'20260211' NOT found in decompressed payload.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    decompress_payload()
