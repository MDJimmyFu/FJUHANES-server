from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
ordseq = "75176750"
hhisnum = "003617083J" # Patient associated with this ordseq in my previous tasks

print(f"[*] Fetching C430 for {ordseq}...")
# I'll use the raw XML response to see all tables
try:
    # Use internal _execute_sql_raw with the facade call pattern
    # Actually, get_pre_anesthesia_data already parses it.
    # I'll modify a local copy to print all table names.
    from lxml import etree
    
    query = f"exec HISOrmC430Facade '{ordseq}','{hhisnum}'"
    res_xml = c._execute_sql_raw(query)
    
    if res_xml:
        root = etree.fromstring(res_xml.encode('utf-8'))
        table_names = set()
        for child in root:
            table_names.add(child.tag)
        
        print(f"[+] Found {len(table_names)} tables in C430 response:")
        for tn in sorted(table_names):
            print(f"  - {tn}")
            # For each table, print a sample row if possible
            rows = root.xpath(f"//{tn}")
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
