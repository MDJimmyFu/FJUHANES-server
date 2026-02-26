import os
import xml.etree.ElementTree as ET
import glob

def parse_labs(file_path):
    print(f"--- {os.path.basename(file_path)} ---")
    try:
        # Some files might have binary junk at the beginning, try to find the start of XML
        with open(file_path, "r", encoding="utf-16", errors="ignore") as f:
            content = f.read()
        
        start_idx = content.find("<diffgr:diffgram")
        if start_idx == -1:
            return
            
        xml_content = content[start_idx:]
        # Extract the relevant part of the XML
        # We'll just use regex or simple search if ET fails on the full thing
        import re
        inspections = re.findall(r'<INSPECTION.*?</INSPECTION>', xml_content, re.DOTALL)
        for ins in inspections:
            title = re.search(r'<TITLE>(.*?)</TITLE>', ins)
            value = re.search(r'<SYB_VALUE>(.*?)</SYB_VALUE>', ins)
            date = re.search(r'<SIGNDATE>(.*?)</SIGNDATE>', ins)
            
            t = title.group(1) if title else "?"
            v = value.group(1) if value else "?"
            d = date.group(1) if date else "?"
            
            print(f"{d} | {t:15} | {v}")
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

files = glob.glob("extracted_0218_78da_*.xml")
for f in files:
    parse_labs(f)
