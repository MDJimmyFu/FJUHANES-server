import sys
import os
import json
import logging

# Set up path to import HISClient
sys.path.append(r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule")
from his_client_final import HISClient

# Initialize client
client = HISClient(
    c250_template=r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\c250_payload_1.bin",
    c430_template=r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\c430_payload_0.bin",
    q050_template=r"c:\Users\A03772\.gemini\antigravity\Combined_Server\SurgerySchedule\q050_payload_0.bin"
)

def analyze_patient():
    print("Target Opdate: 20260220")
    print("Target Patient: 003457263J")
    surgeries = client.get_surgery_list("20260220")
    
    target = next((s for s in surgeries if s.get("HHISTNUM") == "003457263J"), None)
    if not target:
        print("Patient not found in 20260220 C250 response.")
        return
        
    ordseq = target.get("ORDSEQ")
    print(f"Found ORDSEQ: {ordseq}")
    
    print("Activating patient and fetching C430 data...")
    client.activate_patient(ordseq, "003457263J")
    c430 = client.get_pre_anesthesia_data(ordseq, "003457263J", opdate="20260220")
    
    output_path = r"c:\Users\A03772\.gemini\antigravity\scratch\scratch_pre_build_misc\test_pat_003457263J.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"c250": target, "c430": c430}, f, ensure_ascii=False, indent=2)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    analyze_patient()
