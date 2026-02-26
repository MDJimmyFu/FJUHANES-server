from scapy.all import PcapReader, TCP, IP, Raw

def brute_extract(pcap_file, target_indices):
    packets = PcapReader(pcap_file)
    i = 0
    for pkt in packets:
        i += 1
        if i in target_indices and Raw in pkt:
            # We found the packet containing the HEADERS
            # The body might start here or in next packet
            payload = pkt[Raw].load
            header_end = payload.find(b"\r\n\r\n")
            if header_end != -1:
                body = payload[header_end+4:]
            else:
                body = b"" # Headers not finished?
                
            # Now, for HIS requests, the body usually starts with 'x\x00' or similar
            # If we don't see a zlib header (78 9c etc), it might be in the NEXT packet
            print(f"Packet {i} body head: {body[:20].hex()}")
            
            # Save it anyway
            with open(f"brute_req_{i}.bin", "wb") as f:
                f.write(body)

brute_extract("traffic0218.pcapng", [1361, 1445, 1093, 2026])
