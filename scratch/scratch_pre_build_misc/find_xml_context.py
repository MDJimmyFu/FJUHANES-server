def find_context(filename, pattern):
    with open(filename, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if pattern in line:
            print(f"Match on line {i+1}:")
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            for j in range(start, end):
                print(f"{j+1}: {lines[j].strip()}")

find_context("c250_response.xml", "7.94")
