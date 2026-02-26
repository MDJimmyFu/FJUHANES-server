from scapy.all import rdpcap, TCP, Raw
import zlib

def analyze_pcap(pcap_file):
    packets = rdpcap(pcap_file)
    facades = ['HISExmFacade', 'HISOrmC080Facade', 'HISOpoFacade']
    
    for i, packet in enumerate(packets):
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            payload = packet[Raw].load
            
            # Check for HTTP POST
            if b"POST /" in payload:
                try:
                    headers, body = payload.split(b"\r\n\r\n", 1)
                    header_str = headers.decode('utf-8', errors='ignore')
                    
                    found_facade = None
                    for facade in facades:
                        if f"/{facade}" in header_str:
                            found_facade = facade
                            break
                    
                    if found_facade:
                        print(f"\n[+] Found {found_facade} Request (Packet {i})")
                        print("-" * 50)
                        print(header_str)
                        
                        # Try to decompress body if needed (usually checking header, but trying brute force zlib)
                        if b"X-Compress: yes" in payload:    
                            try:
                                decompressed = zlib.decompress(body)
                                print("\nType: Compressed Body")
                                print(f"Decompressed Length: {len(decompressed)}")
                                print("Preview (First 500 bytes):")
                                try:
                                    print(decompressed[:500].decode('utf-8'))
                                except:
                                    print(decompressed[:500])
                            except Exception as e:
                                print(f"\nFailed to decompress: {e}")
                                print("Body Preview:")
                                print(body[:100])
                        else:
                            print("\nType: Raw Body")
                            print(body[:500])
                            
                except Exception as e:
                    pass

analyze_pcap("traffic.pcapng")
