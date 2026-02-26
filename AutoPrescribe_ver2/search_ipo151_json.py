def search():
    with open('intubation.pcapng', 'rb') as f:
        content = f.read()
    
    start = 0
    while True:
        idx = content.find(b'ipoc151ViewJson', start)
        if idx == -1: break
        print(f"Match at {idx}")
        # Show some context
        context = content[max(0, idx-500):idx+500]
        # Check if /IpoC151/Save is nearby
        if b'/IpoC151/Save' in context:
            print("  -> NEAR /IpoC151/Save")
        if b'/IpoC151/ProcessBASOTGP' in context:
            print("  -> NEAR /IpoC151/ProcessBASOTGP")
        
        # Try to find the full POST body if it looks like one
        if b'POST' in context:
             print("  -> POST request found nearby")
        
        start = idx + 1

search()
