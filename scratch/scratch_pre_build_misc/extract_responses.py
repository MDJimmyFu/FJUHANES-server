from scapy.all import PcapReader, TCP, IP, Raw
import zlib

def extract_response_for_req(pcap_file, req_index):
    packets = PcapReader(pcap_file)
    i = 0
    target_key = None
    for pkt in packets:
        i += 1
        if i == req_index and IP in pkt and TCP in pkt:
            target_key = (pkt[IP].dst, pkt[TCP].dport, pkt[IP].src, pkt[TCP].sport)
            continue
            
        if target_key and IP in pkt and TCP in pkt:
            if (pkt[IP].src, pkt[TCP].sport, pkt[IP].dst, pkt[TCP].dport) == target_key:
                if Raw in pkt and b"HTTP/1.1 200 OK" in pkt[Raw].load:
                    print(f"Found response (HTTP 200) in packet {i}")
                    # Follow the stream to get the response body
                    payload = pkt[Raw].load
                    header_end = payload.find(b"\r\n\r\n")
                    body = payload[header_end+4:] if header_end != -1 else b""
                    
                    # Also take the NEXT packet since bodies are large
                    # (Simplified: just take the next few packets in this stream)
                    pass
                
                if Raw in pkt:
                    with open(f"resp_{req_index}_raw.bin", "ab") as f:
                        f.write(pkt[Raw].load)

import sys
if __name__ == "__main__":
    analyze_indices = [int(x) for x in sys.argv[1:]]
    if not analyze_indices:
        print("Usage: python extract_responses.py <index1> <index2> ...")
    else:
        for idx in analyze_indices:
            extract_response_for_req("traffic0218.pcapng", idx)
