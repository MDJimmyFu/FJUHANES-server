import scapy.all as scapy
import zlib
import re
import os

def analyze_pcap(pcap_path):
    print(f"[*] Analyzing {pcap_path}...")
    try:
        packets = scapy.rdpcap(pcap_path)
    except Exception as e:
        print(f"[-] Error reading pcap: {e}")
        return

    sessions = packets.sessions()
    print(f"[*] Found {len(sessions)} sessions.")
    
    for session in sessions:
        payload_data = b""
        session_has_patient = False
        
        for packet in sessions[session]:
            if packet.haslayer(scapy.TCP) and packet.haslayer(scapy.Raw):
                raw = packet[scapy.Raw].load
                payload_data += raw
                if b"003617083J" in raw or b"F129348478" in raw or b"20260215" in raw:
                    session_has_patient = True
        
        if session_has_patient or b"HISOrm" in payload_data:
            print(f"\n[+] Relevant session: {session} (Length: {len(payload_data)})")
            
            # Find all potential zlib starts
            # zlib headers: \x78\x01, \x78\x9c, \x78\xda
            for magic in [b"\x78\x9c", b"\x78\x01", b"\x78\xda"]:
                matches = re.finditer(magic, payload_data)
                for i, match in enumerate(matches):
                    start = match.start()
                    try:
                        decompressed = zlib.decompress(payload_data[start:])
                        text = decompressed.decode('utf-8', errors='replace')
                        
                        # Save if it's longer than a few chars and looks like XML
                        if len(text) > 50 and ("<" in text and ">" in text):
                            filename = f"ext_{session.replace(':', '_').replace(' ', '_')}_{magic[1]}_{i}.xml"
                            with open(filename, "w", encoding="utf-8") as f:
                                f.write(text)
                            print(f"  [*] Saved {magic.hex()} match {i} to {filename} (Len: {len(text)})")
                            
                            # Check keywords
                            for kw in ["003617083J", "WBC", "HB", "HCT", "7.94", "12.2"]:
                                if kw in text:
                                    print(f"    [!] Found KEYWORD: {kw}")
                    except:
                        pass

if __name__ == "__main__":
    pcap_file = "traffic0218.pcapng"
    if os.path.exists(pcap_file):
        analyze_pcap(pcap_file)
    else:
        print(f"[-] {pcap_file} not found.")
