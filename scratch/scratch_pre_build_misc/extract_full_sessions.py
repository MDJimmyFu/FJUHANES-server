from scapy.all import PcapReader, TCP, IP, Raw
import os

def extract_sessions(pcap_file, target_indices):
    print(f"Extracting sessions for indices {target_indices}...")
    packets = PcapReader(pcap_file)
    
    # Map index to session key
    target_sessions = {}
    
    # Store data by session key
    sessions_data = {} # (src, sport, dst, dport) -> bytearray
    
    i = 0
    for pkt in packets:
        i += 1
        if not (IP in pkt and TCP in pkt):
            continue
            
        src = pkt[IP].src
        dst = pkt[IP].dst
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
        key = (src, sport, dst, dport)
        
        # If this is a target packet, mark the session
        # Use a dict to store which index belongs to which key
        if i in target_indices:
            if key not in target_sessions:
                target_sessions[key] = []
            target_sessions[key].append(i)
            
        # Append data to session buffer if we're tracking it
        if key in target_sessions:
            if key not in sessions_data:
                sessions_data[key] = bytearray()
            sessions_data[key].extend(pkt[Raw].load) if Raw in pkt else None

    # Now for each target key, we need to extract the data starting from the correct packet
    # This is getting complex. Let's simplify: 
    # Just save the whole session data and find headers for each target index
    for key, indices in target_sessions.items():
        data = sessions_data.get(key)
        if data:
            # For each target index in this session, the data we want starts at a request header
            # We can find all POST headers in the session data
            all_requests = list(re.finditer(b"POST ", data))
            for j, m_req in enumerate(all_requests):
                # The j-th request in this session
                # We'll just save all of them for now
                body_start = data.find(b"\r\n\r\n", m_req.start())
                if body_start != -1:
                    # Find next request or end
                    next_req = all_requests[j+1].start() if j+1 < len(all_requests) else len(data)
                    body = data[body_start+4:next_req]
                    filename = f"req_session_{key[1]}_{j}.bin"
                    with open(filename, "wb") as f:
                        f.write(body)
                    print(f"Saved session {key[1]} request {j} to {filename} ({len(body)} bytes)")

analyze_indices = [364, 1093, 1361, 1445, 2026]
extract_sessions("traffic0218.pcapng", analyze_indices)
