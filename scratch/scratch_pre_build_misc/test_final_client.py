from his_client_final import HISClient

def verify_labs(pat_id, ordseq):
    client = HISClient()
    print(f"[*] Testing lab retrieval for {pat_id}...")
    data = client.get_pre_anesthesia_data(ordseq, pat_id)
    
    if data and 'INSPECTION' in data:
        print(f"[SUCCESS] Found {len(data['INSPECTION'])} laboratory records!")
        for item in data['INSPECTION'][:5]:
            print(f"  - {item.get('TITLE')}: {item.get('SYB_VALUE')}")
    else:
        print("[-] Laboratory data still missing.")

if __name__ == "__main__":
    verify_labs("003617083J", "A75176986OR0041")
