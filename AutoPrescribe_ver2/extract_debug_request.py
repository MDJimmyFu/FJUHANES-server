import re

def extract(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    
    idx = content.find(b'/IpoC151/Save')
    if idx == -1:
        print(f"Not found in {filename}")
        return
    
    # Backtrack to find start of request (POST)
    req_start = content.rfind(b'POST', 0, idx)
    # Find end of headers
    headers_end = content.find(b'\r\n\r\n', idx)
    if headers_end == -1:
        print("Headers end not found")
        return
    
    headers = content[req_start:headers_end].decode('utf-8', errors='ignore')
    body = content[headers_end+4:headers_end+3000].decode('utf-8', errors='ignore')
    
    with open(f"debug_{filename}.txt", 'w', encoding='utf-8') as out:
        out.write("--- HEADERS ---\n")
        out.write(headers)
        out.write("\n--- BODY ---\n")
        out.write(body)

extract('intubation.pcapng')
extract('intubationinfection.pcapng')
