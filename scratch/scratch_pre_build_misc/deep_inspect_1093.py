import zlib
import re

def deep_inspect_body(filename):
    print(f"--- Deep Inspecting {filename} ---")
    with open(filename, "rb") as f:
        data = f.read()
    
    start = data.find(b"\x78\xda")
    if start != -1:
        data = zlib.decompress(data[start:])
    
    # In HIS datasets, parameters are often serialized.
    # Let's find all strings and see their order.
    matches = re.finditer(rb'[\x20-\x7E]{3,}', data)
    for m in matches:
        print(f"{m.start():04x}: {m.group(0).decode()}")

deep_inspect_body("body_1093.bin")
