from scapy.all import PcapReader, Raw, IP, TCP
import os
import zlib

def find_packet_for_xml(pcap_file, xml_file):
    with open(xml_file, "rb") as f:
        xml_data = f.read()
    
    # Try to find a unique snippet of the response
    # The first 50 bytes of the XML might be enough, but standard XML headers are common.
    # Let's look for something more unique, like a row ID or a specific value.
    target_snippet = b"<INSPECTION diffgr:id=\"INSPECTION25\"" # Contains WBC 7.94 usually
    
    print(f"Searching for {target_snippet} in {pcap_file}...")
    
    packets = PcapReader(pcap_file)
    i = 0
    for pkt in packets:
        i += 1
        if Raw in pkt:
            payload = pkt[Raw].load
            
            # Check raw payload (rarely matches directly if compressed)
            if target_snippet in payload:
                print(f"  [RAW MATCH] Found snippet in packet {i}")
            
            # Check decompressed payload
            for head in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
                start = payload.find(head)
                if start != -1:
                    try:
                        dec = zlib.decompress(payload[start:])
                        if target_snippet in dec:
                            print(f"  [DECOMPRESSED MATCH] Found snippet in packet {i}")
                            print(f"  Session: {pkt[IP].src}:{pkt[TCP].sport} -> {pkt[IP].dst}:{pkt[TCP].dport}")
                    except:
                        continue

find_packet_for_xml("traffic0218.pcapng", "extracted_0218_78da_8.xml")
