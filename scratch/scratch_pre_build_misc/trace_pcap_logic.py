from scapy.all import PcapReader, TCP, IP, Raw
import re
import zlib
import os

def decompress_body(body):
    for head in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
        start = body.find(head)
        if start != -1:
            try:
                return zlib.decompress(body[start:])
            except:
                continue
    return body

def analyze_pcap(pcap_file):
    print(f"Analyzing {pcap_file} for quest/response sequences...")
    packets = PcapReader(pcap_file)
    
    # Simple flow tracking (assuming one conversation at a time for simplicity)
    # real analysis would track by (src_ip, src_port, dst_ip, dst_port)
    
    pending_reprocessing = {} # key: (src, sport, dst, dport), value: last_request_info
    
    results = []
    
    i = 0
    for pkt in packets:
        i += 1
        if not (IP in pkt and TCP in pkt and Raw in pkt):
            continue
            
        payload = pkt[Raw].load
        src = pkt[IP].src
        dst = pkt[IP].dst
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
        
        # Identify Request
        if b"POST " in payload:
            m = re.search(rb"POST (.*?) HTTP", payload)
            if m:
                uri = m.group(1).decode()
                # Find body
                header_end = payload.find(b"\r\n\r\n")
                body = payload[header_end+4:] if header_end != -1 else b""
                
                # Decompress body to see content
                dec_body = decompress_body(body)
                hhistnum = re.search(rb"00\d{7}[A-Z]", dec_body)
                hhistnum_str = hhistnum.group(0).decode() if hhistnum else "Unknown"
                
                pending_reprocessing[(src, sport, dst, dport)] = {
                    'uri': uri,
                    'patient': hhistnum_str,
                    'packet_index': i
                }
        
        # Identify Response (simplistic: look for HTTP/1.1 200)
        elif b"HTTP/1.1 200 OK" in payload:
            key = (dst, dport, src, sport) # Flip ports for response
            if key in pending_reprocessing:
                req_info = pending_reprocessing[key]
                
                # Check for INSPECTION in response
                # Note: response might be chunked/multi-packet. This only checks the first packet.
                header_end = payload.find(b"\r\n\r\n")
                resp_body = payload[header_end+4:] if header_end != -1 else b""
                dec_resp = decompress_body(resp_body)
                
                has_inspection = b"<INSPECTION" in dec_resp
                
                print(f"Request {req_info['packet_index']}: {req_info['uri']} for {req_info['patient']} -> Response has INSPECTION: {has_inspection}")
                
                if has_inspection:
                    print(f"  [!!!!] FOUND LAB DATA FOR {req_info['patient']} in {req_info['uri']}")
                
                results.append({
                    'req': req_info,
                    'has_inspection': has_inspection
                })
                del pending_reprocessing[key]

analyze_pcap("traffic0218.pcapng")
