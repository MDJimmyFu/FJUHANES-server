import json
import urllib.parse
import re

def analyze():
    with open('debug_save_653.bin', 'rb') as f:
        data = f.read()
    
    # Let's just print the whole snippet as printable text
    printable = "".join([chr(b) if 32 <= b <= 126 else "." for b in data])
    print(printable)

analyze()
