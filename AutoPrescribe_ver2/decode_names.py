import re

def extract_names(filename):
    print(f"--- {filename} ---")
    with open(filename, 'rb') as f:
        content = f.read()
    
    codes = [b'TR001210', b'TR001209']
    for code in codes:
        idx = content.find(code)
        while idx != -1:
            # Look for OrdProced nearby
            start = max(0, idx - 500)
            end = min(len(content), idx + 500)
            snippet = content[start:end]
            m = re.search(br'"OrdProced":"(.*?)"', snippet)
            if m:
                # Try Big5 then UTF-8
                raw_name = m.group(1)
                try:
                    name_big5 = raw_name.decode('big5')
                    print(f"Code {code.decode()}: {name_big5} (Big5)")
                except:
                    pass
                try:
                    name_utf8 = raw_name.decode('utf-8')
                    print(f"Code {code.decode()}: {name_utf8} (UTF-8)")
                except:
                    pass
                break # Just find first for each code
            idx = content.find(code, idx + 1)

extract_names('intubation.pcapng')
extract_names('intubationinfection.pcapng')
