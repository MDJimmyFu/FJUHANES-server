import scapy.all as scapy
import zlib
import re
import os

def extract_response_from_session(pcap_path):
    print(f"[*] Analyzing {pcap_path}...")
    packets = scapy.rdpcap(pcap_path)
    
    # Find the packet closest to the offset
    target_packet = None
    for p in packets:
        if p.haslayer(scapy.Raw) and b"HISOrmC430Facade" in p[scapy.Raw].load:
            target_packet = p
            break
    
    if not target_packet:
        print("[-] Target packet with HISOrmC430Facade not found.")
        return

    sport = target_packet[scapy.TCP].sport
    dport = target_packet[scapy.TCP].dport
    src = target_packet[scapy.IP].src
    dst = target_packet[scapy.IP].dst
    
    print(f"[*] Session: {src}:{sport} -> {dst}:{dport}")
    
    response_payload = b""
    capturing = False
    for p in packets:
        if p.haslayer(scapy.IP) and p.haslayer(scapy.TCP):
            if p[scapy.IP].src == dst and p[scapy.IP].dst == src and \
               p[scapy.TCP].sport == dport and p[scapy.TCP].dport == sport:
                if p.haslayer(scapy.Raw):
                    load = p[scapy.Raw].load
                    if b"HTTP/1.1 200 OK" in load:
                        capturing = True
                    if capturing:
                        response_payload += load

    if response_payload:
        print(f"[*] Extracted response payload (Len: {len(response_payload)})")
        with open("raw_response_0218.bin", "wb") as f:
            f.write(response_payload)
        
        # Search for ASCII keywords
        for kw in [b"003617083J", b"WBC", b"HB", b"7.94", b"12.2", b"INSPECTION"]:
            if kw in response_payload:
                print(f"    [!] Found {kw} in raw response!")

        # Try to find ALL zlib starts (78 01, 78 9c, 78 da)
        for magic in [b"\x78\x9c", b"\x78\x01", b"\x78\xda"]:
            matches = re.finditer(magic, response_payload)
            for i, match in enumerate(matches):
                start = match.start()
                try:
                    dec = zlib.decompress(response_payload[start:])
                    text = dec.decode('utf-8', errors='replace')
                    print(f"    [+] Found {magic.hex()} zlib at {start}. Decompressed len: {len(text)}")
                    if "WBC" in text or "003617083J" in text or "HB" in text:
                        filename = f"extracted_0218_{magic.hex()}_{i}.xml"
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(text)
                        print(f"    [*] Saved to {filename}")
                except: pass
    else:
        print("[-] No response payload found for this session.")

if __name__ == "__main__":
    pcap_file = "traffic0218.pcapng"
    extract_response_from_session(pcap_file)
