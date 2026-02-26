from scapy.all import PcapReader, TCP, IP, Raw

def extract_facades(pcap_file):
    import zlib
    
    print(f"Scanning {pcap_file} for facades...")
    try:
        packets = PcapReader(pcap_file)
    except Exception as e:
        print(f"Error reading pcap: {e}")
        return

    sessions = {} 
    # 1. Group payloads by flow
    for pkt in packets:
        if IP in pkt and TCP in pkt and Raw in pkt:
            key = (pkt[IP].src, pkt[TCP].sport, pkt[IP].dst, pkt[TCP].dport)
            if key not in sessions:
                sessions[key] = bytearray()
            sessions[key].extend(pkt[Raw].load)
            
    print(f"Reassembled {len(sessions)} TCP streams.")

    targets = ['HISExmFacade', 'HISOrmC080Facade', 'HISOpoFacade']
    
    for key, payload in sessions.items():
        payload_bytes = bytes(payload) # safer for finding
        
        for target in targets:
            target_bytes = f"POST /{target}".encode()
            if target_bytes in payload_bytes:
                print(f"[+] Found {target} in stream {key}")
                
                # Find multiple requests in same stream?
                parts = payload_bytes.split(target_bytes)
                
                # parts[0] is garbage before first request (or empty)
                # parts[1+] serve as start of requests
                
                for i, part in enumerate(parts[1:]):
                     # Prepend "POST /target" back
                     full_req = target_bytes + part
                     
                     header_end = full_req.find(b"\r\n\r\n")
                     if header_end != -1:
                         headers = full_req[:header_end].decode(errors='ignore')
                         # Parse Content-Length
                         import re
                         cl_match = re.search(r'Content-Length: (\d+)', headers, re.IGNORECASE)
                         if cl_match:
                             cl = int(cl_match.group(1))
                             body_start = header_end + 4
                             body = full_req[body_start : body_start + cl]
                             
                             filename = f"{target}_payload_{i}.bin"
                             with open(filename, "wb") as f:
                                 f.write(body)
                             print(f"    Saved {len(body)} bytes to {filename}")
                             
                             # Try Decompress
                             try:
                                 d = zlib.decompress(body)
                                 print(f"    Decompressed: {d[:200]}")
                                 dec_filename = f"{target}_decoded_{i}.xml"
                                 with open(dec_filename, "wb") as f:
                                     f.write(d)
                             except:
                                 print("    Decompression failed (maybe not zlib?)")

if __name__ == "__main__":
    extract_facades("traffic.pcapng")
