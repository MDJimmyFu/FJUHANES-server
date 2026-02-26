from his_client_final import HISClient
import sys, json
import xml.etree.ElementTree as ET

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
ordseq = "75176750"
hhisnum = "003617083J"

print(f"[*] Fetching C430 for {ordseq}...")
try:
    query = f"exec HISOrmC430Facade '{ordseq}','{hhisnum}'"
    res_xml = c._execute_sql_raw(query)
    
    if res_xml:
        root = ET.fromstring(res_xml)
        table_names = set()
        for child in root:
            table_names.add(child.tag)
        
        print(f"[+] Found {len(table_names)} tables in C430 response:")
        for tn in sorted(table_names):
            print(f"  - {tn}")
            rows = root.findall(f".//{tn}")
            if rows:
                print(f"    Sample Columns: {[c.tag for c in rows[0]]}")
                # If table looks like it has clinical notes, print content
                if any(x in tn.upper() for x in ['MEMO', 'REPORT', 'NOTE', 'DIAG', 'EXAM', 'CLINIC']):
                     for col in rows[0]:
                         if col.text: print(f"      {col.tag}: {col.text[:100]}")
    else:
        print("[-] No response from C430.")
except Exception as e:
    print(f"[-] Error: {e}")
