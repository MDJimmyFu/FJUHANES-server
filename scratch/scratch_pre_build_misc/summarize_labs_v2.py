import os
import re
import glob

def parse_labs(file_path):
    print(f"--- {os.path.basename(file_path)} ---")
    try:
        # Read as bytes first to avoid encoding issues
        with open(file_path, "rb") as f:
            blob = f.read()
        
        # Try to decode as utf-16 (little or big endian) or utf-8
        content = None
        for enc in ['utf-16', 'utf-16-le', 'utf-16-be', 'utf-8']:
            try:
                content = blob.decode(enc)
                break
            except:
                continue
        
        if not content:
            print("Failed to decode file.")
            return

        # Find all INSPECTION blocks
        # Looking for <INSPECTION ...> ... </INSPECTION>
        inspections = re.findall(r'<INSPECTION.*?</INSPECTION>', content, re.DOTALL)
        for ins in inspections:
            title = re.search(r'<TITLE>(.*?)</TITLE>', ins)
            value = re.search(r'<SYB_VALUE>(.*?)</SYB_VALUE>', ins)
            date = re.search(r'<SIGNDATE>(.*?)</SIGNDATE>', ins)
            
            t = title.group(1) if title else "?"
            v = value.group(1) if value else "?"
            d = date.group(1) if date else "?"
            
            print(f"{d} | {t:15} | {v}")
            
        # Also search for the specific unique values in the raw content just in case
        unique_values = ["342", "11.2", "29.3", "1.01", "9.2", "105", "139"]
        for uv in unique_values:
            if uv in content:
                print(f"[FOUND UNIQUE VALUE] {uv} exists in this file")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

files = glob.glob("extracted_0218_78da_*.xml")
for f in files:
    parse_labs(f)
