import struct

def search_patterns():
    with open("c250_payload_1.bin", "rb") as f:
        data = f.read()
    
    patterns = [
        b"20260211",
        b"2026/02/11",
        b"1150211", # ROC Year
        b"115/02/11",
        "20260211".encode('utf-16le'),
        "2026/02/11".encode('utf-16le'),
        "2026-02-11".encode('utf-16le'),
        # Ticks?
        # A DateTime in .NET binary serialization is often Int64 ticks.
        # 2026-02-11 00:00:00 = 639064320000000000 ticks
        # We can look for Int64 close to this value.
    ]
    
    for p in patterns:
        idx = data.find(p)
        if idx != -1:
            print(f"Found {p} at index {idx}")
            
    # Heuristic for ticks:
    # Look for any 8-byte sequence that decodes to a reasonable DateTime
    print("Searching for DateTime ticks...")
    import datetime
    for i in range(len(data) - 8):
        chunk = data[i:i+8]
        try:
            val = struct.unpack("<q", chunk)[0]
            # Ticks are 100-nanosecond intervals since 0001-01-01
            # 2026 is approx 6.39e17
            if 630000000000000000 < val < 650000000000000000:
                dt = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=val/10)
                print(f"Index {i}: Found tick value {val} -> {dt}")
        except:
            pass

if __name__ == "__main__":
    search_patterns()
