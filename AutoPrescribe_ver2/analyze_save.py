import json
import urllib.parse
import re

def analyze():
    with open('debug_save_body.bin', 'rb') as f:
        data = f.read()
    
    # Body usually starts after \r\n\r\n
    headers_end = data.find(b'\r\n\r\n')
    if headers_end == -1:
        print("Header end not found in snippet.")
        # Try finding parameter start
        idx = data.find(b'hHISNum=')
        if idx == -1: return
        body = data[idx:]
    else:
        body = data[headers_end+4:]

    # It might be followed by more TCP headers if it was truncated/split
    # Let's just find where it ends (usually end of string or next request)
    # But for now, let's just split by &
    params = body.split(b'&')
    for p in params:
        if b'=' not in p: continue
        try:
            name, val = p.split(b'=', 1)
            name_str = name.decode('utf-8', errors='ignore')
            # The value might have trailing garbage from pcap, let's be careful
            val_str = urllib.parse.unquote_plus(val.decode('utf-8', errors='ignore'))
            
            if name_str in ['ipoc151ViewJson', 'ipoc151View']:
                # Find the JSON part more cleanly (ends with ] or })
                match_json = re.search(r'^[\[\{].*?[\}\]]', val_str)
                if match_json:
                    val_str = match_json.group(0)
                
                try:
                    parsed = json.loads(val_str)
                    print(f"--- {name_str} ---")
                    if isinstance(parsed, list):
                        for i, item in enumerate(parsed):
                            print(f"  Item {i}:")
                            for k, v in item.items():
                                print(f"    {k}: {v}")
                    else:
                        for k, v in parsed.items():
                            print(f"  {k}: {v}")
                except:
                    print(f"--- {name_str} (JSON FAIL) ---")
                    print(val_str[:500])
            else:
                # Clean up value from trailing garbage
                clean_val = val_str.split('\r')[0].split('\n')[0].split(' ')[0]
                print(f"{name_str}: {clean_val}")
        except:
            pass

analyze()
