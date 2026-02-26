import json
import sys

def extract(filename):
    print(f"--- {filename} ---")
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    parts = content.split('ipoc151ViewJson":"[')
    if len(parts) > 1:
        for p in parts[1:]:
            end_idx = p.find(']"')
            if end_idx != -1:
                s_raw = '[' + p[:end_idx] + ']'
                s_unescaped = s_raw.replace('\\\\"', '"')
                try:
                    data = json.loads(s_unescaped)
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
                    print("==========")
                except Exception as e:
                    print(f"JSON Parse Error: {e}")
                    pass

extract('search_intubation.txt')
extract('search_intub_inf.txt')
