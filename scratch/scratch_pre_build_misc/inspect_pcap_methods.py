from scapy.all import PcapReader, TCP, IP, Raw
import re
import zlib

def decompress_body(body):
    for head in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
        start = body.find(head)
        if start != -1:
            try:
                return zlib.decompress(body[start:])
            except:
                continue
    return body

def analyze_methods(pcap_file):
    print(f"Extracting methods and patients from {pcap_file}...")
    packets = PcapReader(pcap_file)
    i = 0
    for pkt in packets:
        i += 1
        if not (IP in pkt and TCP in pkt and Raw in pkt):
            continue
            
        payload = pkt[Raw].load
        if b"POST " in payload:
            m = re.search(rb"POST (.*?) HTTP", payload)
            if m:
                uri = m.group(1).decode()
                header_end = payload.find(b"\r\n\r\n")
                body = payload[header_end+4:] if header_end != -1 else b""
                dec_body = decompress_body(body)
                
                # Try to find method name in decompressed body
                # Usually look for string after 'GetData' or similar
                # Or just look for any ASCII strings longer than 5 chars
                method = "Unknown"
                # Patterns like: GetData, GetSelectTable, GetDBData followed by method name
                # In HIS packets, the method name is often in the first few strings.
                strs = re.findall(rb'[A-Za-z0-9_]{5,}', dec_body)
                if strs:
                    # Filter out common junk
                    candidates = [s.decode() for s in strs if b"Facade" not in s and b"Version" not in s]
                    if candidates:
                        method = candidates[0]
                
                hhistnum = re.search(rb"00\d{7}[A-Z]", dec_body)
                hhistnum_str = hhistnum.group(0).decode() if hhistnum else ""
                
                print(f"[{i:5}] {uri} -> Method: {method} | Pat: {hhistnum_str}")

analyze_methods("traffic0218.pcapng")
