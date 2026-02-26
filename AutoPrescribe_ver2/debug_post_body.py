import re
import sys

filename = sys.argv[1]

with open(filename, 'rb') as f:
    content = f.read()

# Look for POST /Ipo/IpoC151/Save
idx = content.find(b'POST /Ipo/IpoC151/Save')
if idx != -1:
    print(f"--- Found POST in {filename} ---")
    # Body usually starts after \r\n\r\n
    body_start = content.find(b'\r\n\r\n', idx)
    if body_start != -1:
        body = content[body_start+4:body_start+5000] # take a good chunk
        # Try to find the end of the HTTP request or just print printable
        printable = "".join([chr(b) if 32 <= b <= 126 else "." for b in body])
        print(printable)
else:
    print(f"POST /Ipo/IpoC151/Save not found in {filename}")
