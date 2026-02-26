import zlib
import re

def print_all_strings(filename):
    print(f"--- All Strings in {filename} ---")
    with open(filename, "rb") as f:
        data = f.read()
    
    start = data.find(b"\x78\xda")
    if start != -1:
        try:
            data = zlib.decompress(data[start:])
        except:
            pass
    
    matches = re.finditer(rb'[\x20-\x7E]{3,}', data)
    for m in matches:
        print(f"{m.start():04x}: {m.group(0).decode()}")

print_all_strings("body_1361.bin")
