import re
import urllib.parse
import json

def extract_ipoc151(filename):
    print(f"--- {filename} ---")
    with open(filename, 'rb') as f:
        content = f.read()
    
    # Try finding as JSON property
    matches = re.finditer(b'ipoc151ViewJson":"(\\[.*?\\])"', content)
    found = False
    for m in matches:
        try:
            s_raw = m.group(1).decode('utf-8', errors='ignore')
            s_unescaped = s_raw.replace('\\\\"', '"')
            data = json.loads(s_unescaped)
            print("FOUND as JSON property:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
            found = True
        except:
            pass
    
    # Try finding as form-encoded data
    matches = re.finditer(b'ipoc151ViewJson=(.*?)&', content)
    for m in matches:
        try:
            s_raw = m.group(1).decode('utf-8', errors='ignore')
            decoded = urllib.parse.unquote_plus(s_raw)
            data = json.loads(decoded)
            print("FOUND as Form-encoded:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
            found = True
        except:
            pass
            
    if not found:
        print("No ipoc151ViewJson found with these patterns.")

extract_ipoc151('intubation.pcapng')
extract_ipoc151('intubationinfection.pcapng')
