import re

def extract_ipoc151_details(filename):
    print(f"--- {filename} ---")
    with open(filename, 'rb') as f:
        content = f.read()
    
    # regex to find ipoc151ViewJson content
    # it's usually inside a JSON object or as a form field
    # In the pcap it looks like: ipoc151ViewJson":"[...]
    matches = re.finditer(b'ipoc151ViewJson":"(\\[.*?\\])"', content)
    for m in matches:
        try:
            s_raw = m.group(1).decode('utf-8', errors='ignore')
            s_unescaped = s_raw.replace('\\\\"', '"')
            # Extract TRTCode and OrdProced manually if JSON fails or just to be quick
            trt_code = re.search(r'"TRTCode":"(.*?)"', s_unescaped)
            proc_name = re.search(r'"OrdProced":"(.*?)"', s_unescaped)
            remark = re.search(r'"TRRemark":"(.*?)"', s_unescaped)
            from_set = re.search(r'"FromOrderSet":"(.*?)"', s_unescaped)
            
            print(f"TRTCode: {trt_code.group(1) if trt_code else 'N/A'}")
            # Proc name might be messed up due to encoding in my print, but let's see
            print(f"OrdProced: {proc_name.group(1) if proc_name else 'N/A'}")
            print(f"Remark: {remark.group(1) if remark else 'N/A'}")
            print(f"FromOrderSet: {from_set.group(1) if from_set else 'N/A'}")
            print("-" * 10)
        except:
            pass

extract_ipoc151_details('intubation.pcapng')
extract_ipoc151_details('intubationinfection.pcapng')
