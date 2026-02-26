from scapy.all import PcapReader, TCP, IP, Raw
import re
import os

def extract_q050_payloads(pcap_file, target_uri="/HISOrmQ050Facade"):
    print(f"Scanning {pcap_file} for {target_uri}...")
    try:
        packets = PcapReader(pcap_file)
    except Exception as e:
        print(f"Error reading pcap: {e}")
        return

    sessions = {} # Key: (src_ip, src_port, dst_ip, dst_port), Value: bytearray

    # 1. Group payloads by flow
    for pkt in packets:
        if IP in pkt and TCP in pkt and Raw in pkt:
            key = (pkt[IP].src, pkt[TCP].sport, pkt[IP].dst, pkt[TCP].dport)
            if key not in sessions:
                sessions[key] = bytearray()
            sessions[key].extend(pkt[Raw].load)
            
    print(f"Reassembled {len(sessions)} TCP streams.")

    # 2. Search for the target request in reassembled streams
    count = 0
    for key, payload in sessions.items():
        current_pos = 0
        while True:
            target_pos = payload.find(target_uri.encode(), current_pos)
            if target_pos == -1:
                break
                
            # Backtrack to find "POST " (method start)
            method_pos = payload.rfind(b"POST ", 0, target_pos)
            if method_pos == -1:
                current_pos = target_pos + 1
                continue
                
            # Check headers
            header_end = payload.find(b"\r\n\r\n", target_pos)
            if header_end != -1:
                 headers_raw = payload[method_pos:header_end]
                 headers_str = headers_raw.decode(errors='ignore')
                 
                 cl_match = re.search(r'Content-Length: (\d+)', headers_str, re.IGNORECASE)
                 body_start = header_end + 4
                 
                 if cl_match:
                     content_length = int(cl_match.group(1))
                     body = payload[body_start : body_start + content_length]
                     print(f"[{count}] Found POST {target_uri} in stream {key}")
                     print(f"    Content-Length: {content_length}")
                     
                     filename = f"q050_payload_{count}.bin"
                     with open(filename, "wb") as f:
                         f.write(body)
                     print(f"    Saved payload to {filename}")
                     count += 1
                     current_pos = body_start + content_length
                 else:
                     print(f"[{count}] Found POST {target_uri} but no Content-Length found.")
                     current_pos = header_end + 4
            else:
                 current_pos = target_pos + 1
                 
    if count == 0:
        print(f"No requests found for {target_uri}")

if __name__ == "__main__":
    extract_q050_payloads("traffic.pcapng")
