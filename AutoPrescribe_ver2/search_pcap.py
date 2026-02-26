import re
import sys
import json

filename = sys.argv[1]

with open(filename, 'rb') as f:
    content = f.read()

# try to decode with Big5 and UTF-8 to find keywords
keywords = [b'Intubat', b'intubat', "氣管".encode('utf-8'), "插管".encode('utf-8'), "氣管".encode('big5', errors='ignore'), "插管".encode('big5', errors='ignore')]

print("Searching in", filename)
# find indices
for kw in keywords:
    idx = content.find(kw)
    while idx != -1:
        start = max(0, idx - 200)
        end = min(len(content), idx + 500)
        snippet = content[start:end]
        try:
            print("--- Found keyword ---")
            print(snippet.decode('utf-8', errors='ignore'))
            print("---------------------")
        except:
            pass
        idx = content.find(kw, idx + 1)
