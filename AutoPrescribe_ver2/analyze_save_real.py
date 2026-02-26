def analyze():
    with open('debug_save_real.bin', 'rb') as f:
        data = f.read()
    
    # Headers then body
    idx = data.find(b'\r\n\r\n')
    if idx != -1:
        print("--- HEADERS ---")
        print(data[:idx].decode('utf-8', errors='ignore'))
        print("--- BODY ---")
        # Try to decode as JSON
        body = data[idx+4:]
        try:
             import json
             # Body might be followed by more data, try to find end of JSON
             json_str = body.decode('utf-8', errors='ignore')
             # Find matching braces
             brace_count = 0
             end_idx = 0
             for i, c in enumerate(json_str):
                 if c == '{': brace_count += 1
                 elif c == '}': brace_count -= 1
                 if brace_count == 0 and i > 0:
                     end_idx = i + 1
                     break
             if end_idx > 0:
                 json_obj = json.loads(json_str[:end_idx])
                 print(json.dumps(json_obj, indent=2, ensure_ascii=False))
             else:
                 print(json_str[:500])
        except Exception as e:
             print(f"Decode error: {e}")
             print(body[:500])

analyze()
