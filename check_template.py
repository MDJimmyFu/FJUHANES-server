import zlib
import os
import re

template_path = r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\q050_payload_0.bin"

if os.path.exists(template_path):
    with open(template_path, "rb") as f:
        compressed = f.read()
    try:
        decompressed = zlib.decompress(compressed)
        print(f"Decompressed size: {len(decompressed)}")
        
        # Look for potential hhistnum patterns
        hhist_matches = re.findall(rb'\d{9}[A-Z]', decompressed)
        print(f"Found HHISTNUM-like patterns: {hhist_matches}")
        
        # Look for potential ordseq patterns
        ordseq_matches = re.findall(rb'[A-Z]\d{8,10}OR\d{4,6}', decompressed)
        print(f"Found ORDSEQ-like patterns: {ordseq_matches}")
        
    except Exception as e:
        print(f"Error: {e}")
else:
    print("File not found")
