import re

with open("c250_response.xml", "r", encoding='utf-8', errors='replace') as f:
    text = f.read()

# Find all ORDOP_OPSTA blocks
blocks = re.findall(r'<ORDOP_OPSTA[^>]*>(.*?)</ORDOP_OPSTA>', text, re.DOTALL)
print(f"Found {len(blocks)} blocks.")

for i, block in enumerate(blocks[:10]):
    print(f"\n--- Block {i} ---")
    tags = re.findall(r'<(\w+)>(.*?)</\1>', block)
    for tag, value in tags:
        if any(k in tag for k in ["TIME", "DTTM", "MIN", "STATUS", "ST"]):
            print(f"{tag}: {value}")
