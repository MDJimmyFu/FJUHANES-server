import zlib
import os

q050_path = r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\q050_payload_0.bin"
c250_path = r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\c250_activate.bin"

def verify_replace(path, targets):
    if not os.path.exists(path):
        print(f"File {path} not found")
        return
    with open(path, "rb") as f:
        compressed = f.read()
    decompressed = zlib.decompress(compressed)
    
    all_ok = True
    for target in targets:
        count = decompressed.count(target)
        print(f"Target {target} in {os.path.basename(path)}: {count} times")
        if count == 0:
            all_ok = False
    return all_ok

print("Verifying Q050 (Anesthesia Charging Detail):")
q050_ok = verify_replace(q050_path, [b"003162935D", b"A75072943OR0001"])

print("\nVerifying C250 (Patient Activation):")
c250_ok = verify_replace(c250_path, [b"A129523047"])

if q050_ok and c250_ok:
    print("\nSUCCESS: All template strings found and will be replaced correctly.")
else:
    print("\nFAILURE: Some template strings were not found.")
