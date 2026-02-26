import os
import re
import glob

def parse_labs(file_path):
    # print(f"--- {os.path.basename(file_path)} ---")
    try:
        with open(file_path, "rb") as f:
            blob = f.read()
        
        content = None
        for enc in ['utf-16-le', 'utf-16', 'utf-8']:
            try:
                content = blob.decode(enc)
                break
            except:
                continue
        
        if not content:
            return
            
        patients = re.findall(r'<HHISTNUM>(.*?)</HHISTNUM>', content)
        has_inspection = '<INSPECTION' in content
        
        if has_inspection:
            print(f"File: {os.path.basename(file_path)}")
            print(f"  Patients: {set(patients)}")
            # Count rows
            rows = re.findall(r'<INSPECTION.*?</INSPECTION>', content, re.DOTALL)
            print(f"  INSPECTION count: {len(rows)}")
            if rows:
                # Sample one row
                title = re.search(r'<TITLE>(.*?)</TITLE>', rows[0])
                val = re.search(r'<SYB_VALUE>(.*?)</SYB_VALUE>', rows[0])
                print(f"  Sample Row: {title.group(1) if title else '?'} = {val.group(1) if val else '?'}")
            print("-" * 20)

    except Exception as e:
        pass

files = glob.glob("extracted_0218_78da_*.xml")
# Sort by number
files.sort(key=lambda x: int(re.search(r'(\d+)', x).group(1)) if re.search(r'(\d+)', x) else 0)

for f in files:
    parse_labs(f)
