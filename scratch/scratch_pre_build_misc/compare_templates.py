import zlib
import re

def get_strings(filename):
    with open(filename, "rb") as f:
        data = f.read()
    start = data.find(b"\x78\xda")
    if start != -1:
        data = zlib.decompress(data[start:])
    
    matches = re.findall(rb'[\x20-\x7E]{3,}', data)
    return set(m.decode('ascii', errors='ignore') for m in matches)

s1445 = get_strings("body_1445.bin")
sTemp = get_strings("c430_payload_0.bin")

print("--- Strings in 1445 but NOT in template ---")
diff1 = sorted(list(s1445 - sTemp))
for s in diff1:
    print(s)

print("\n--- Strings in template but NOT in 1445 ---")
diff2 = sorted(list(sTemp - s1445))
for s in diff2:
    print(s)
