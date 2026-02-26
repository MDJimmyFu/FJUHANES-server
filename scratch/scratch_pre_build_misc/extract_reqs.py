from scapy.all import PcapReader, TCP, IP, Raw
import zlib

def extract_specific_requests(pcap_file, indices):
    packets = PcapReader(pcap_file)
    i = 0
    for pkt in packets:
        i += 1
        if i in indices and Raw in pkt:
            payload = pkt[Raw].load
            header_end = payload.find(b"\r\n\r\n")
            body = payload[header_end+4:] if header_end != -1 else b""
            
            filename = f"req_{i}.bin"
            with open(filename, "wb") as f:
                f.write(body)
            print(f"Saved request {i} to {filename} ({len(body)} bytes)")

extract_specific_requests("traffic0218.pcapng", [1445, 2026, 1361])
