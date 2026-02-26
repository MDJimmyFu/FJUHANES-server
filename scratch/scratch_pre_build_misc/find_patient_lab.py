import re

with open("extracted_0218_78da_8.xml", "rb") as f:
    blob = f.read()
    
for enc in ['utf-16', 'utf-16-le', 'utf-8']:
    try:
        content = blob.decode(enc)
        break
    except:
        continue

# Find all patients in the file
patients = re.findall(r'<HHISTNUM>(.*?)</HHISTNUM>', content)
print(f"Total HHISTNUM entries: {len(set(patients))}")
print(f"Unique Patient IDs: {set(patients)}")

# Find all INSPECTION blocks and the nearest preceding HHISTNUM
blocks = re.split(r'(<INSPECTION.*?</INSPECTION>)', content, flags=re.DOTALL)
current_patient = "Unknown"
for b in blocks:
    patient_match = re.search(r'<HHISTNUM>(.*?)</HHISTNUM>', b)
    if patient_match:
        current_patient = patient_match.group(1)
    
    if '<INSPECTION' in b:
        if '7.94' in b:
            print(f"[MATCH] WBC 7.94 found for Patient: {current_patient}")
            # Also print the whole block for context
            title = re.search(r'<TITLE>(.*?)</TITLE>', b)
            value = re.search(r'<SYB_VALUE>(.*?)</SYB_VALUE>', b)
            print(f"  Row: {title.group(1) if title else '?'} = {value.group(1) if value else '?'}")

