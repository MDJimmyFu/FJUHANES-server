import json
import re

def analyze_file(filename):
    print(f"=== Analyzing {filename} ===")
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Search for ipoc151ViewJson
    idx = data.find(b'ipoc151ViewJson')
    if idx != -1:
        print(f"Found ipoc151ViewJson at {idx}")
        # Find start of JSON [ or {
        blob = data[idx:]
        start = blob.find(b'[')
        if start == -1: start = blob.find(b'{')
        
        if start != -1:
            json_blob = blob[start:]
            # Find end
            bc = 0
            end = 0
            for i, b in enumerate(json_blob):
                if b == ord('[') or b == ord('{'): bc += 1
                elif b == ord(']') or b == ord('}'): bc -= 1
                if bc == 0 and i > 0:
                    end = i + 1
                    break
            
            if end > 0:
                try:
                    js = json.loads(json_blob[:end].decode('utf-8', errors='ignore'))
                    # If it's a list, it's probably the orders
                    if isinstance(js, list):
                        for item in js:
                            print(f"  Code: {item.get('TRTCode')} | Name: {item.get('OrdProced') or item.get('TRTName')}")
                    else:
                        print(json.dumps(js, indent=2, ensure_ascii=False))
                except:
                    print("JSON Decode Failed")
                    print(json_blob[:500])
        else:
            print("No JSON start found")
    else:
        print("ipoc151ViewJson not found")

analyze_file('painless_process_context.bin')
analyze_file('painless_save_context.bin')
