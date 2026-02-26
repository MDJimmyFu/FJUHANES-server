import re
import sys

filename = sys.argv[1]

with open(filename, 'rb') as f:
    content = f.read()

# find all printable strings > 30 chars
strings = re.findall(b'[\\x20-\\x7E]{30,}', content)

print(f"--- Extracting from {filename} ---")
for s in strings:
    try:
        s_str = s.decode('utf-8')
        if 'ipoC11CViewsJson' in s_str or 'OrdProced' in s_str or 'CacheOrder' in s_str or 'setDrgCode' in s_str:
            # We want to catch the main payload saving the order
            print(s_str[:500])
            print("...")
    except:
        pass
