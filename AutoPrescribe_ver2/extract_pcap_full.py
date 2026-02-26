import re
import json
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else 'pcea.pcapng'
with open(filename, 'rb') as f:
    content = f.read()

# To handle UTF-8 JSON payloads properly
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Find string that starts with {"recordID" and contains "basostds"
match = re.search(br'\\{"recordID":"[^"]+","hHISNum":"[^"]+","hCaseNo":"[^"]+","basostds":\\[.*?\\]\\}', content, re.DOTALL)
if match:
    try:
        s = match.group(0).decode('utf-8')
        data = json.loads(s)
        print("--- basostds ---")
        for item_str in data['basostds']:
            item = json.loads(item_str)
            print(item.get('OSTItem'), item.get('OSTItemNM'), item.get('Dose'), item.get('Route'), item.get('OSTCode'), item.get('sKey'))
    except Exception as e:
        print("Json parse error:", e)

# Find ipoC11CViewsJson
match2 = re.search(br'ipoC11CViewsJson":"(\\[\\{\\"OrdSeq\\".*?\\}\\])"', content, re.DOTALL)
if match2:
    try:
        # It's a stringified JSON inside JSON, so we need to decode escapes or just parse the whole thing
        s2 = match2.group(1).decode('utf-8').replace('\\\\"', '"')
        data2 = json.loads(s2)
        print("\\n--- ipoC11CViewsJson ---")
        for item in data2:
            print("UDOGivRoute:", item.get("UDOGivRoute"))
            print("UDOGivDose:", item.get("UDOGivDose"))
            print("OrdProced:", item.get("OrdProced"))
    except Exception as e:
        print("Json parse error 2:", e)

