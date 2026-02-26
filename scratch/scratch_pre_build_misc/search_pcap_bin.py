import os

def search_binary(file_path, search_bytes):
    if not os.path.exists(file_path):
        print(f"[-] {file_path} not found.")
        return
    
    with open(file_path, "rb") as f:
        content = f.read()
    
    index = content.find(search_bytes)
    if index != -1:
        print(f"[+] Found {search_bytes} at offset {index}")
        # Print some context around it
        start = max(0, index - 100)
        end = min(len(content), index + 100)
        context = content[start:end]
        print(f"    Context: {context}")
        return True
    else:
        print(f"[-] {search_bytes} not found.")
        return False

if __name__ == "__main__":
    pcap = "traffic0218.pcapng"
    search_binary(pcap, b"003617083J")
    search_binary(pcap, b"3617083") # Substring
    search_binary(pcap, b"F129348478")
    search_binary(pcap, b"129348478") # Substring
    search_binary(pcap, b"20260215")
    search_binary(pcap, b"HISOrmC430Facade")
    search_binary(pcap, b"HISOrmC250Facade")
