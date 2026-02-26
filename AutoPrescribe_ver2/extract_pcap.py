import re
import json

with open('pcea.pcapng', 'rb') as f:
    content = f.read()

# find { ... } that look like json, at least 50 chars
# regex to find `{...` ignoring internal structure, simple heuristic
matches = re.finditer(b'\\{[^{}]+\\}', content)

with open('payloads.txt', 'w', encoding='utf-8') as out:
    # try a wider regex for JSON objects
    # actually, all HTTP bodies in this HIS application are visible as ASCII/UTF-8
    # let's just extract all strings and filter for JSON
    strings = re.findall(b'[\\x20-\\x7E]{20,}', content)
    for s in strings:
        try:
            s_str = s.decode('utf-8')
            if 'basostds' in s_str or 'rxCodes' in s_str or 'ipoC11CViewsJson' in s_str:
                out.write(s_str + '\\n')
        except:
            pass
