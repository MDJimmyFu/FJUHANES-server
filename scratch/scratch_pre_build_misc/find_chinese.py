import zlib
import re

def find_chinese():
    try:
        with open("c250_response.bin", "rb") as f:
            data = f.read()
        
        decompressed = zlib.decompress(data)
        
        # Look for <HNAMEC>...<HNAMEC> blocks where content has high bytes
        print("Scanning for Chinese names...")
        
        # We'll use a byte regex.
        # Tag: <HNAMEC> is 3c484e414d45433e
        # content
        # </HNAMEC> is 3c2f484e414d45433e
        
        # Regex: b'<HNAMEC>(.*?)</HNAMEC>'
        matches = re.finditer(b'<HNAMEC>(.*?)</HNAMEC>', decompressed)
        
        count = 0
        for m in matches:
            content = m.group(1)
            # Check if it has non-ascii
            if any(b > 127 for b in content):
                print(f"\nMatch {count}:")
                print(f"Hex: {content.hex()}")
                
                for enc in ['utf-8', 'big5', 'cp950', 'gbk']:
                    try:
                        decoded = content.decode(enc)
                        print(f"  {enc}: {decoded}")
                    except:
                        print(f"  {enc}: (failed)")
                count += 1
                if count > 5: break
        
        if count == 0:
            print("No non-ASCII HNAMEC found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_chinese()
