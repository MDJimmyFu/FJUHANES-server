import json
import urllib.parse

def analyze():
    with open('debug_dump.bin', 'rb') as f:
        data = f.read()
    
    # The data starts with /IpoC151/Save...
    # The POST body follows after a gap
    # Let's just find "hHISNum="
    idx = data.find(b'hHISNum=')
    if idx == -1:
        print("Could not find POST body in dump.")
        return
    
    body = data[idx:]
    # Split by &
    params = body.split(b'&')
    for p in params:
        try:
            name, val = p.split(b'=', 1)
            name_str = name.decode()
            val_str = urllib.parse.unquote_plus(val.decode('utf-8', errors='ignore'))
            
            if name_str in ['ipoc151ViewJson', 'ipoc151View']:
                parsed = json.loads(val_str)
                print(f"--- {name_str} ---")
                if isinstance(parsed, list) and len(parsed) > 0:
                    item = parsed[0]
                    for k, v in item.items():
                        print(f"  {k}: {type(v).__name__} = {v if not isinstance(v, str) or len(v) < 50 else v[:50] + '...'}")
                else:
                    for k, v in parsed.items():
                        print(f"  {k}: {type(v).__name__} = {v}")
            else:
                print(f"{name_str}: {val_str}")
        except Exception as e:
            # print("error", e)
            pass

analyze()
