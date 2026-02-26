import re
import json

def extract(filename):
    print(f"--- {filename} ---")
    with open(filename, 'rb') as f:
        content = f.read()
    
    # Search for ipoc151ViewJson followed by stringified array
    matches = re.finditer(b'ipoc151ViewJson":"(\\[\\\\{\\\\"OrdSeq.*?\\])"', content, re.DOTALL)
    for m in matches:
        try:
            s_raw = m.group(1).decode('utf-8', errors='ignore')
            # The string might have extra trailing stuff if regex is greedy, but we used non-greedy .*?
            # Actually, let's just find the first matching bracket or just unescape
            s_unescaped = s_raw.replace('\\\\"', '"')
            data = json.loads(s_unescaped)
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
            print("==========")
        except Exception as e:
            # print("error", e)
            pass

extract('intubation.pcapng')
extract('intubationinfection.pcapng')
