def extract_payloads(filename, offsets):
    with open(filename, 'rb') as f:
        content = f.read()
    
    for offset in offsets:
        print(f"--- Offset {offset} ---")
        # Read a chunk around the offset
        chunk = content[offset:offset+2000]
        # Look for JSON starting after \r\n\r\n or just search for { or [
        # In previously analyzed PCAPs, it was application/json
        start_json = chunk.find(b'{')
        if start_json == -1:
            start_json = chunk.find(b'[')
        
        if start_json != -1:
            json_blob = chunk[start_json:]
            # Try to find the end of the JSON object
            brace_count = 0
            end_idx = 0
            for i, b in enumerate(json_blob):
                if b == ord('{') or b == ord('['):
                    brace_count += 1
                elif b == ord('}') or b == ord(']'):
                    brace_count -= 1
                
                if brace_count == 0 and i > 0:
                    end_idx = i + 1
                    break
            
            if end_idx > 0:
                try:
                    import json
                    parsed = json.loads(json_blob[:end_idx].decode('utf-8', errors='ignore'))
                    print(json.dumps(parsed, indent=2, ensure_ascii=False))
                except:
                    print(json_blob[:end_idx].decode('utf-8', errors='ignore'))
            else:
                print("Could not find end of JSON")
        else:
            print("Could not find start of JSON")

extract_payloads('painless.pcapng', [1197551, 1338643])
