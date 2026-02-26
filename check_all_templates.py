import zlib
import os
import re

templates = [
    r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\q050_payload_0.bin",
    r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\c430_payload_0.bin",
    r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\c250_payload_1.bin",
    r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\c250_activate.bin"
]

for template_path in templates:
    if os.path.exists(template_path):
        print(f"\nChecking {os.path.basename(template_path)}...")
        with open(template_path, "rb") as f:
            compressed = f.read()
        try:
            decompressed = zlib.decompress(compressed)
            print(f"  Decompressed size: {len(decompressed)}")
            
            hhist_matches = re.findall(rb'\d{9}[A-Z]', decompressed)
            print(f"  Found HHISTNUM-like patterns: {hhist_matches}")
            
            ordseq_matches = re.findall(rb'[A-Z]\d{8,10}OR\d{4,6}', decompressed)
            print(f"  Found ORDSEQ-like patterns: {ordseq_matches}")
            
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print(f"\nFile not found: {template_path}")
