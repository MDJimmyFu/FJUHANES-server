import re, sys, io

# Set stdout to utf-8 to avoid encoding errors on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = "template_c430_final.txt"
try:
    with open(file_path, "r", encoding="utf-16le") as f:
        content = f.read()
    
    # Extract strings like <TABLE_NAME> or just uppercase names
    # Usually datasets have table names in <Table> structure
    table_names = sorted(list(set(re.findall(r'<([A-Z0_9_]+)', content))))
    
    print(f"[*] Found {len(table_names)} potential table tags in {file_path}:")
    for name in table_names:
        if any(keyword in name for keyword in ['REPORT', 'RPT', 'IMG', 'RADIO', 'EKG', 'ECG', 'CXR', 'INSPECTION']):
            print(f"  MATCH: {name}")
        elif len(name) > 3:
             # print(name)
             pass

    # Specifically look for common report table names if not found
    for extra in ['RADIO_IMG_RPT', 'EKG_RPT', 'REPORT']:
        if extra in content:
            print(f"  FOUND STRING: {extra}")

except Exception as e:
    print(f"Error reading file: {e}")
