from scapy.all import PcapReader, Raw, IP, TCP

def dump_headers(pcap_file, index):
    packets = PcapReader(pcap_file)
    i = 0
    for pkt in packets:
        i += 1
        if i == index and Raw in pkt:
            payload = pkt[Raw].load
            header_end = payload.find(b"\r\n\r\n")
            if header_end != -1:
                print(payload[:header_end+4].decode('ascii', errors='ignore'))
            else:
                print("Could not find end of headers in this packet.")

dump_headers("traffic0218.pcapng", 1445)
