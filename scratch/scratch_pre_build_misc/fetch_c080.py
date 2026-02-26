import requests
import zlib
import datetime

class HISClientC080:
    def __init__(self, template_file="HISOrmC080Facade_payload_0.bin"):
        self.base_url = "http://10.10.246.90:8800"
        self.template_file = template_file
        self.headers = {
            "Content-Type": "application/octet-stream",
            "X-Compress": "yes",
            "User-Agent": "Mozilla/4.0+(compatible; MSIE 6.0; Windows 6.2.9200.0; MS .NET Remoting; MS .NET CLR 2.0.50727.9164 )",
            "Expect": "100-continue",
            "Host": "10.10.246.90:8800",
            "Connection": "Keep-Alive"
        }

    def get_c080_data(self, hhistnum):
        print(f"[*] Fetching C080 data for {hhistnum}...")
        try:
            with open(self.template_file, "rb") as f:
                compressed_template = f.read()
            
            # Try to decompress to verify/patch
            try:
                decompressed = zlib.decompress(compressed_template)
            except:
                # If template is raw binary (not compressed yet) or just header
                # Based on previous dump, it was compressed.
                print("[-] Template decompression failed, trying to use as is if not compressed.")
                decompressed = compressed_template

            # Template has HHISNUM '003162935D'
            target_bytes = hhistnum.encode('ascii')
            template_bytes = b"003162935D"
            
            if template_bytes not in decompressed:
                 # Check if the extracted payload was actually the *request* payload.
                 # Packet 12118 was POST /HISOrmC080Facade.
                 # The decompressed file was 'HISOrmC080Facade_decoded_0.xml'.
                 # Let's check if we can just simple replace.
                 print(f"[-] Warning: Template HHISTNUM {template_bytes} not found. Dumping first 100 bytes...")
                 print(decompressed[:100])
                 # It might be UTF-16 or something?
                 # XML dump showed plain text.
            
            patched_payload = decompressed.replace(template_bytes, target_bytes)
            
            # Recompress?
            # If the original was compressed, we recompress.
            # analyze_new_endpoints.py showed X-Compress: yes.
            final_payload = zlib.compress(patched_payload)
            
            response = requests.post(f"{self.base_url}/HISOrmC080Facade", data=final_payload, headers=self.headers)
            response.raise_for_status()
            
            print(f"[*] Response Status: {response.status_code}")
            return response.content
            
        except Exception as e:
            print(f"[-] Error fetching C080 data: {e}")
            return None

    def parse_response(self, content):
        if not content: return
        try:
            decompressed = zlib.decompress(content)
            decoded = decompressed.decode('utf-8', errors='ignore')
            
            # Print full XML (it might be large, but we need to see it)
            # Find the start of XML
            start = decoded.find("<?xml")
            if start != -1:
                print("\n--- Full XML Response ---")
                print(decoded[start:])
            else:
                print("\n--- Full Response (No XML found) ---")
                print(decoded)
            
        except Exception as e:
            print(f"[-] Error parsing response: {e}")

if __name__ == "__main__":
    client = HISClientC080()
    # Target Patient
    hhistnum = "003617083J" 
    data = client.get_c080_data(hhistnum)
    client.parse_response(data)
