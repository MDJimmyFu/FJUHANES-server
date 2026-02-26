import re

def extract_names(filename):
    print(f"--- {filename} ---")
    with open(filename, 'rb') as f:
        content = f.read()
    
    # Common TR codes in HIS usually start with TR0012
    codes = [b'TR001200', b'TR001206', b'TR001230', b'TR001231', b'TR001232', 
             b'TR001233', b'TR001234', b'TR001235', b'TR001238', b'TR001239']
    
    for code in codes:
        idx = content.find(code)
        if idx != -1:
            # Look for "TRTName":"..." or nearby text
            snippet = content[idx-100:idx+300]
            # Try to find a pattern like "TRTName":"..."
            match = re.search(b'"TRTName":"([^"]+)"', snippet)
            if match:
                print(f"Code {code.decode()}: {match.group(1).decode('utf-8', errors='ignore')}")
            else:
                # Just print printable chars around it
                match_generic = re.search(b'":"([^"]+)"', snippet)
                if match_generic:
                     print(f"Code {code.decode()}: {match_generic.group(1).decode('utf-8', errors='ignore')}")
                else:
                     print(f"Code {code.decode()}: (No name found in snippet)")

extract_names('painless.pcapng')
