from his_client_final import HISClient
import json

def verify_full_fallback(hhistnum, ordseq):
    client = HISClient()
    user_id = 'A03772'
    
    print(f"=== Verifying Full Fallback for {hhistnum} / {ordseq} ===")
    
    # Simulate app.py flow
    client.activate_patient(ordseq, hhistnum)
    pre_data = client.get_pre_anesthesia_data(ordseq, hhistnum)
    
    # We want to see how it maps. 
    # Even if some are already present in VITALSIGNUPLOAD, 
    # we want to ensure any missing fields are filled.
    vitals = client.get_vitals_from_exm(hhistnum, ordseq, user_id=user_id, pre_data=pre_data)
    
    print("\nResulting Vitals:")
    print(json.dumps(vitals, indent=2))
    
    check_fields = ['HEIGHT', 'WEIGHT', 'BT', 'BP', 'PULSE', 'RESP', 'SPO2']
    missing = [f for f in check_fields if not vitals.get(f) or vitals[f] == '0']
    
    if not missing:
        print("\n[SUCCESS] All vital signs are present!")
        # Check if C430 marker is there for BP if it fell back
        if '(C430)' in vitals.get('BP', ''):
             print("[INFO] BP fell back to C430 as expected (if it was missing).")
    else:
        print(f"\n[FAILURE] Still missing: {missing}")

if __name__ == "__main__":
    verify_full_fallback("003616525A", "A75176715OR0001")
