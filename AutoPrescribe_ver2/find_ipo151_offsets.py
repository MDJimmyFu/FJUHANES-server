import re

def find_offsets(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    
    print(f"--- {filename} ---")
    for m in [b'POST /Ipo/IpoC151/ProcessBASOTGP', b'POST /Ipo/IpoC151/Save']:
        offsets = [i for i in range(len(content)) if content.startswith(m, i)]
        print(f"{m.decode()}: {len(offsets)} matches at {offsets}")

find_offsets('intubation.pcapng')
find_offsets('intubationinfection.pcapng')
