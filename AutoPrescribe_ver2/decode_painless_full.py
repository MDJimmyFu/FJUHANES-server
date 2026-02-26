import json
import re

def analyze():
    with open('painless_save_context.bin', 'rb') as f:
        data = f.read()
    
    # Try to find ipoc151ViewJson string value
    # Pattern: "ipoc151ViewJson":"[...]"
    match = re.search(b'"ipoc151ViewJson":"(\\[.*?\\])"', data)
    if match:
        json_str_escaped = match.group(1).decode('utf-8', errors='ignore')
        # Unescape \" to "
        json_str = json_str_escaped.replace('\\"', '"')
        try:
            items = json.loads(json_str)
            print("--- Painless Labor Treatment Orders ---")
            for i, item in enumerate(items):
                print(f"Order {i}:")
                print(f"  Code: {item.get('TRTCode')}")
                print(f"  Name: {item.get('OrdProced')}")
                print(f"  Freq: {item.get('TRFreqn')}")
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            print(json_str[:1000])
    else:
        print("Could not find escaped JSON array for ipoc151ViewJson")

analyze()
