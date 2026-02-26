from scapy.all import PcapReader, TCP, IP, Raw
import re

def analyze_pcap(pcap_file):
    print(f"Analyzing {pcap_file}...")
    try:
        packets = PcapReader(pcap_file)
    except Exception as e:
        print(f"Error reading pcap: {e}")
        return

    http_traffic = []

    for pkt in packets:
        if IP in pkt and TCP in pkt and Raw in pkt:
            payload = pkt[Raw].load
            try:
                payload_str = payload.decode('utf-8', errors='ignore')
                
                # Check for HTTP generic methods
                if re.match(r'^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH) ', payload_str):
                    # Extract Host header
                    host_match = re.search(r'Host: (.+?)\r\n', payload_str, re.IGNORECASE)
                    host = host_match.group(1) if host_match else "Unknown"
                    
                    # Store if interesting host (or catch-all for now to see what's there)
                    # We are looking for auth.fjcuh.org.tw or internal IPs
                    if "fjcuh" in host or "10." in host or "192.168." in host or "172." in host:
                        http_traffic.append({
                            "src": pkt[IP].src,
                            "dst": pkt[IP].dst,
                            "host": host,
                            "payload": payload_str[:500] # Capture first 500 chars (headers + start of body)
                        })
                
                elif payload_str.startswith("HTTP/"):
                     # Response
                     pass

            except Exception as e:
                continue

    print(f"Found {len(http_traffic)} interesting HTTP requests.")
    for traffic in http_traffic:
        print("-" * 40)
        print(f"Host: {traffic['host']}")
        print(f"Src: {traffic['src']} -> Dst: {traffic['dst']}")
        print("Payload Preview:")
        print(traffic['payload'])
        print("-" * 40)

if __name__ == "__main__":
    analyze_pcap("traffic.pcapng")
