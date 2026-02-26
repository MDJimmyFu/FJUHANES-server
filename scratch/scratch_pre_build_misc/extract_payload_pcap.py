from scapy.all import PcapReader, TCP, IP, Raw
import re

def extract_payload(pcap_file, target_uri):
    print(f"Scanning {pcap_file} for {target_uri}...")
    try:
        packets = PcapReader(pcap_file)
    except Exception as e:
        print(f"Error reading pcap: {e}")
        return

    count = 0
    for pkt in packets:
        if IP in pkt and TCP in pkt and Raw in pkt:
            payload = pkt[Raw].load
            # Check if this packet contains the headers for the target request
            # Note: This simple check assumes headers and body start in the same packet
            # or at least the URI is present.
            try:
                # We need to look for the method line
                if target_uri.encode() in payload and b"POST " in payload:
                    print(f"Found request to {target_uri}")
                    
                    # Find the end of headers
                    header_end = payload.find(b"\r\n\r\n")
                    if header_end != -1:
                        body = payload[header_end+4:]
                        if len(body) > 0:
                            filename = f"c250_request_{count}.bin"
                            with open(filename, "wb") as f:
                                f.write(body)
                            print(f"Saved {len(body)} bytes to {filename}")
                            count += 1
                        else:
                            print("Found headers but body seems empty or in next packet (not handling reassembly yet).")
                    else:
                         print("Could not find end of headers.")
            except Exception as e:
                print(f"Error processing packet: {e}")
                continue

if __name__ == "__main__":
    extract_payload("traffic.pcapng", "/HISOrmC250Facade")
