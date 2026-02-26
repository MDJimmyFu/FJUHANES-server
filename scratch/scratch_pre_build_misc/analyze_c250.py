import zlib
import re

def analyze_c250():
    try:
        with open('c250_payload_1.bin', 'rb') as f:
            data = zlib.decompress(f.read())
            
        print("Length of decompressed payload:", len(data))
        
        # Look for dates like 2026XXXX
        dates_found = re.findall(b'2026\\d{4}', data)
        print("Dates found in payload:", set(dates_found))
        
        # Look around 20260211
        idx = data.find(b'20260211')
        while idx != -1:
            start = max(0, idx - 50)
            end = min(len(data), idx + 50)
            print(f"Context at {idx}:")
            print(data[start:end])
            idx = data.find(b'20260211', idx + 1)
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    analyze_c250()
