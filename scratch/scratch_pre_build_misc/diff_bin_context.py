def diff_binary(file1, file2):
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        b1 = f1.read()
        b2 = f2.read()
    
    if len(b1) != len(b2):
        print(f"Size mismatch: {len(b1)} vs {len(b2)}")
        limit = min(len(b1), len(b2))
    else:
        limit = len(b1)
        
    diffs = 0
    for i in range(limit):
        if b1[i] != b2[i]:
            diffs += 1
            if diffs < 100:
                # Show context
                start = max(0, i - 16)
                end = min(limit, i + 16)
                print(f"Diff at offset {i:04x}: {b1[i]:02x} vs {b2[i]:02x}")
                print(f"  Context 1: {b1[start:end].hex()}")
                print(f"  Context 2: {b2[start:end].hex()}")
            elif diffs == 100:
                print("Too many diffs...")
    
    print(f"Total diffs: {diffs}")

diff_binary("norm_1445.bin", "norm_temp.bin")
