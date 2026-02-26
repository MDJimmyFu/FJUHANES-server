def search_vital_signs():
    with open('painless.pcapng', 'rb') as f:
        content = f.read()
    
    # Search for "生命徵象" (Vital Sign)
    # UTF-8: \xe7\x94\x9f\xe5\x91\xbd\xe5\xbe\xb5\xe8\xb1\xa1
    # Big5: \xa5\xcd\xa1\xda\xbc\x7b\x20 (approximate)
    
    search_terms = {
        "生命徵象 (UTF-8)": "生命徵象".encode('utf-8'),
        "生命徵象 (Big5)": "生命徵象".encode('big5', errors='ignore'),
        "Vital Sign": b"Vital Sign",
        "TR0012": b"TR0012"
    }

    for name, term in search_terms.items():
        if not term: continue
        matches = [i for i in range(len(content)) if content.startswith(term, i)]
        print(f"{name}: Found {len(matches)} matches")
        if matches:
            print(f"  First 3 matches: {matches[:3]}")

search_vital_signs()
