from scapy.all import PcapReader, TCP, IP, Raw

def extract_body_next(pcap_file, target_indices):
    packets = PcapReader(pcap_file)
    i = 0
    targets = set(target_indices)
    active_sessions = {} # key -> next_packet_should_be_body
    
    for pkt in packets:
        i += 1
        if not (IP in pkt and TCP in pkt):
            continue
            
        src = pkt[IP].src
        dst = pkt[IP].dst
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
        key = (src, sport, dst, dport)
        
        # If we are waiting for a body in this session
        if key in active_sessions:
            if Raw in pkt:
                filename = f"body_{active_sessions[key]}.bin"
                with open(filename, "wb") as f:
                    f.write(pkt[Raw].load)
                print(f"Saved body for packet {active_sessions[key]} to {filename}")
            del active_sessions[key]
            
        # If this is a header packet
        if i in targets:
            active_sessions[key] = i

import sys
if __name__ == "__main__":
    analyze_indices = [int(x) for x in sys.argv[1:]]
    if not analyze_indices:
        print("Usage: python extract_body_next.py <index1> <index2> ...")
    else:
        extract_body_next("traffic0218.pcapng", analyze_indices)
