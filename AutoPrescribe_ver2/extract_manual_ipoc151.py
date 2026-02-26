import json

def extract_manual(filename):
    print(f"--- {filename} ---")
    with open(filename, 'rb') as f:
        content = f.read()
    
    start_search = 0
    while True:
        idx = content.find(b'ipoc151ViewJson', start_search)
        if idx == -1:
            break
        
        # Find the next '['
        bracket_start = content.find(b'[', idx)
        if bracket_start == -1 or bracket_start - idx > 50:
            start_search = idx + 1
            continue
            
        # Find the matching ']'
        # To avoid early exit with nested brackets (though here it's usually flat), let's just find the next ']' that is followed by '"' or '&' or '}'
        bracket_end = content.find(b']', bracket_start)
        if bracket_end == -1:
            start_search = idx + 1
            continue
            
        payload_bytes = content[bracket_start:bracket_end+1]
        try:
            s = payload_bytes.decode('utf-8', errors='ignore')
            # The payload usually has escaped quotes: \"
            # Let's fix those
            s_fixed = s.replace('\\"', '"').replace('\\\\"', '"')
            # Try to parse it
            data = json.loads(s_fixed)
            print("FOUND PAYLOAD:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
            print("=" * 20)
        except Exception as e:
            # print(f"Error at {idx}: {e}")
            # If it's not JSON, maybe it's URL-encoded?
            pass
            
        start_search = idx + 1

extract_manual('intubation.pcapng')
extract_manual('intubationinfection.pcapng')
