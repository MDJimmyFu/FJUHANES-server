import zlib

def normalize_and_save(filename, out_name, replacements):
    with open(filename, "rb") as f:
        data = f.read()
    start = data.find(b"\x78\xda")
    if start != -1:
        data = zlib.decompress(data[start:])
    
    for old, new in replacements:
        data = data.replace(old, new)
        
    with open(out_name, "wb") as f:
        f.write(data)

# Replacements to normalize 1445 to template values
# 1445: 003617083J, A75176986OR0041, \\DC2, fe80::c84e:ad5c:9185:fbec%11
# Temp: 003356125A, A75176778OR0001, \\DC1, fe80::1b3c:207f:b089:dc8%17
reps = [
    (b"003617083J", b"003356125A"),
    (b"A75176986OR0041", b"A75176778OR0001"),
    (b"20260218", b"20260212"),
    (b"\\\\DC2", b"\\\\DC1"),
    (b"fe80::c84e:ad5c:9185:fbec%11", b"fe80::1b3c:207f:b089:dc8%17")
]

normalize_and_save("body_1445.bin", "norm_1445.bin", reps)
normalize_and_save("c430_payload_0.bin", "norm_temp.bin", [])

print("Normalized files saved. Use fc or diff.")
