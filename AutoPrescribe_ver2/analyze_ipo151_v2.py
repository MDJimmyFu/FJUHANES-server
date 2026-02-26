import json
import urllib.parse
import re

def analyze():
    with open('debug_body.bin', 'rb') as f:
        data = f.read()
    
    # Try to find the start of the form parameters
    # The string might be inside a JSON or form-encoded
    # If it's form encoded, it starts with hHISNum=...
    match = re.search(b'hHISNum=.*?&ipoc151ViewJson=', data)
    if not match:
        print("Could not find standard form pattern. Printing raw around ipoc151ViewJson...")
        idx = data.find(b'ipoc151ViewJson')
        print(data[idx-100:idx+500].decode('utf-8', errors='ignore'))
        return

    body = data[match.start():]
    params = body.split(b'&')
    for p in params:
        if b'=' not in p: continue
        name, val = p.split(b'=', 1)
        name_str = name.decode()
        # Decode URL first
        try:
            val_str = urllib.parse.unquote_plus(val.decode('utf-8', errors='ignore'))
            
            if name_str in ['ipoc151ViewJson', 'ipoc151View']:
                parsed = json.loads(val_str)
                print(f"--- {name_str} ---")
                if isinstance(parsed, list):
                    item = parsed[0]
                    for k, v in item.items():
                        print(f"  {k}: {type(v).__name__} = {v}")
                else:
                    for k, v in parsed.items():
                        print(f"  {k}: {type(v).__name__} = {v}")
            else:
                print(f"{name_str}: {val_str}")
        except:
            pass

analyze()
