import zlib
import os
import re

def check_file(path, label):
    if not os.path.exists(path):
        print(f"\nFile not found: {path}")
        return
    print(f"\nChecking {label} ({os.path.basename(path)})...")
    with open(path, "rb") as f:
        compressed = f.read()
    try:
        decompressed = zlib.decompress(compressed)
        print(f"  Decompressed size: {len(decompressed)}")
        
        # Check specific strings
        targets = [b"003356125A", b"A75176778OR0001", b"20260211", b"003162935D", b"A75072943OR0001"]
        for t in targets:
            print(f"  Found '{t}': {t in decompressed}")
            
        # If not found, look for similar patterns
        print("  Common Patterns:")
        print(f"    Dates (YYYYMMDD): {re.findall(rb'202\d{5}', decompressed)}")
        print(f"    HHISTNUM (\d{{9}}[A-Z]): {re.findall(rb'\d{9}[A-Z]', decompressed)}")
        print(f"    ORDSEQ ([A-Z]\d{{8,10}}OR\d{{4,6}}): {re.findall(rb'[A-Z]\d{8,10}OR\d{4,6}', decompressed)}")

    except Exception as e:
        print(f"  Error: {e}")

check_file(r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\c250_payload_1.bin", "Surgery List")
check_file(r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\c250_activate.bin", "Activate Patient")
check_file(r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\q050_payload_0.bin", "Anesthesia Charging")
check_file(r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\c430_payload_0.bin", "Pre-Anesthesia Data")
