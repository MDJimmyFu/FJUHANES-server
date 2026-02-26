import json
import zlib
import base64

har_path = r"C:\Users\A03772\.gemini\antigravity\scratch\traffic.har"

def analyze_response():
    print(f"Loading HAR: {har_path}")
    try:
        with open(har_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    entries = data['log']['entries']
    for entry in entries:
        req = entry['request']
        if "HISOrmC250Facade" in req['url']:
            print(f"\nRequest: {req['url']}")
            resp = entry['response']
            print(f"Response Status: {resp['status']}")
            
            content = resp['content']
            text = content.get('text', '')
            encoding = content.get('encoding', '')
            
            print(f"Resp Encoding: {encoding}")
            print(f"Resp Text Len: {len(text)}")
            
            raw_bytes = None
            if encoding == 'base64':
                try:
                    raw_bytes = base64.b64decode(text)
                except Exception as e:
                    print(f"Base64 decode failed: {e}")
            else:
                # Maybe it is just text?
                print("Response text repr preview: " + repr(text[:50]))
                
            if raw_bytes:
                print(f"Raw Bytes Len: {len(raw_bytes)}")
                print(f"Header: {raw_bytes[:4].hex()}")
                
                # Try zlib
                try:
                    decompressed = zlib.decompress(raw_bytes)
                    print("SUCCESS: Decompressed Response!")
                    
                    # Look for keywords
                    decompressed_str = decompressed.decode('utf-8', errors='replace')
                    keywords = ["Surgery", "Operation", "Date", "Patient", "OR_DATE", "OP_DATE"]
                    for k in keywords:
                        if k in decompressed_str:
                            print(f"Found keyword by substring: {k}")
                    
                    print("-" * 20 + " PREVIEW " + "-" * 20)
                    # Write to file instead of print to avoid encoding errors
                    with open("c250_response.xml", "wb") as f_out:
                        f_out.write(decompressed)
                    print("Saved decompressed response to c250_response.xml")
                    
                except Exception as e:
                    print(f"Decompress failed: {e}")

if __name__ == "__main__":
    analyze_response()
