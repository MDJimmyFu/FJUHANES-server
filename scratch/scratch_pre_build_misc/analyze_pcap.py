
import subprocess
import json
import binascii

def analyze_pcap(filename, search_terms):
    tshark_path = r"C:\Program Files\Wireshark\tshark.exe"
    command = [
        tshark_path, "-r", filename,
        "-Y", 'http.request or http.response',
        "-T", "json",
        "-e", "frame.number",
        "-e", "http.request.method",
        "-e", "http.request.uri",
        "-e", "http.file_data",
        "-e", "http.response.code"
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running tshark: {result.stderr}")
        return

    packets = json.loads(result.stdout)
    
    for pkt in packets:
        source = pkt.get("_source", {})
        layers = source.get("layers", {})
        
        frame_num = layers.get("frame.number", [""])[0]
        method = layers.get("http.request.method", [""])[0]
        uri = layers.get("http.request.uri", [""])[0]
        file_data_hex = layers.get("http.file_data", [""])[0]
        
        if file_data_hex:
            try:
                # remove colons if present
                clean_hex = file_data_hex.replace(":", "")
                data_bytes = binascii.unhexlify(clean_hex)
                # Try to decode as utf-8 or cp950 (Big5) common in Taiwan
                try:
                    data_str = data_bytes.decode('utf-8')
                except:
                    try:
                        data_str = data_bytes.decode('cp950')
                    except:
                        data_str = str(data_bytes)
                
                for term in search_terms:
                    if term.lower() in data_str.lower() or term.lower() in uri.lower():
                        print(f"--- Frame {frame_num} ---")
                        print(f"Method: {method}, URI: {uri}")
                        print(f"Found term '{term}' in data:")
                        print(data_str[:1000]) # Print first 1000 chars
                        print("-" * 20)
            except Exception as e:
                pass

if __name__ == "__main__":
    search_terms = ["PCA", "Painless", "減痛", "無痛", "分娩", "IpoC11GSave", "FEN02", "Epidural"]
    print("Analyzing PCA.pcapng...")
    analyze_pcap("PCA.pcapng", search_terms)
    print("\nAnalyzing painless.pcapng...")
    analyze_pcap("painless.pcapng", search_terms)
