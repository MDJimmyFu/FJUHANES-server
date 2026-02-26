import sys

def extract_raw(filename):
    print(f"--- {filename} ---")
    with open(filename, 'rb') as f:
        content = f.read()
    
    start_pos = 0
    while True:
        pos = content.find(b'ipoc151ViewJson', start_pos)
        if pos == -1:
            break
        # Take a large chunk after the keyword
        chunk = content[pos:pos+3000]
        try:
            # Clean up non-printable for display
            display = "".join([chr(b) if 32 <= b <= 126 else "." for b in chunk])
            print(display)
            print("-" * 20)
        except:
            pass
        start_pos = pos + 1

extract_raw('intubation.pcapng')
extract_raw('intubationinfection.pcapng')
