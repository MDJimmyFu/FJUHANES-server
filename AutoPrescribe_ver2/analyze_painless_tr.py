def analyze_painless():
    with open('painless.pcapng', 'rb') as f:
        content = f.read()
    
    # Common TR codes in HIS usually start with TR00
    import re
    tr_codes = re.findall(b'TR[0-9]{6}', content)
    unique_tr = sorted(list(set(tr_codes)))
    print("Found TR codes:", [c.decode() for c in unique_tr])

    # Check for IpoC151 calls
    for m in [b'/Ipo/IpoC151/ProcessBASOTGP', b'/Ipo/IpoC151/Save']:
        offsets = [i for i in range(len(content)) if content.startswith(m, i)]
        print(f"{m.decode()} matches at: {offsets}")

analyze_painless()
