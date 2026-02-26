import requests
import zlib
import datetime
import re
import os
import sys

class HISPreAnesthesiaClient:
    def __init__(self, payload_template_path="c430_payload_0.bin"):
        self.url = "http://10.10.246.90:8800/HISOrmC430Facade"
        self.payload_template_path = payload_template_path
        self.headers = {
            "Content-Type": "application/octet-stream",
            "X-Compress": "yes",
            "User-Agent": "Mozilla/4.0+(compatible; MSIE 6.0; Windows 6.2.9200.0; MS .NET Remoting; MS .NET CLR 2.0.50727.9164 )",
            "Expect": "100-continue",
            "Host": "10.10.246.90:8800",
            "Connection": "Keep-Alive"
        }

    def get_data(self, date_str=None):
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            
        print(f"[*] Fetching pre-anesthesia data for {date_str}...")
        
        # 1. Prepare Payload
        try:
            with open(self.payload_template_path, "rb") as f:
                compressed_template = f.read()
            
            decompressed = zlib.decompress(compressed_template)
            
            # Use same date patching logic
            template_date = b"20260211"
            
            if template_date not in decompressed:
                print("[-] Warning: Template payload does not contain 20260211. Date patching might fail.")
                # It might use a different date or no date.
                # Let's check for any date.
                pass
                
            target_date_bytes = date_str.encode('ascii')
            patched_payload = decompressed.replace(template_date, target_date_bytes)
            
            final_payload = zlib.compress(patched_payload)
            
        except Exception as e:
            print(f"[-] Payload preparation error: {e}")
            return None

        # 2. Send Request
        try:
            response = requests.post(self.url, data=final_payload, headers=self.headers)
            print(f"Status: {response.status_code}, Size: {len(response.content)}")
            
            if response.status_code == 200:
                self._parse_response(response.content)
            else:
                print("[-] Request failed.")
                
        except requests.exceptions.RequestException as e:
            print(f"[-] Network error: {e}")

    def _parse_response(self, content):
        try:
            decompressed = zlib.decompress(content)
            text = decompressed.decode('utf-8', errors='replace')
            
            # Debug: Print structure
            if "diffgr:diffgram" in text:
                print("[+] Found DataSet in response.")
                
                # Try to identify main tag name. 
                # Usually it's like <ORDOP_OPSTA> or <PreAnes...>
                # Let's look for tags inside NewDataSet
                match = re.search(r'<NewDataSet>(.*?)</NewDataSet>', text, re.DOTALL)
                if match:
                    inner = match.group(1)
                    # Find first tag
                    tag_match = re.search(r'<(\w+)\s+diffgr:id', inner)
                    if tag_match:
                        print(f"[+] Identified Row Tag: {tag_match.group(1)}")
                        
                        rows = re.findall(f'<{tag_match.group(1)}[^>]*>(.*?)</{tag_match.group(1)}>', text, re.DOTALL)
                        print(f"[+] Found {len(rows)} entries.")
                        
                        # Print ID and Name if possible
                        for i, row in enumerate(rows[:5]):
                            print(f"\n--- Entry {i+1} ---")
                            # Extract everything that looks like a value
                            fields = re.findall(r'<(\w+)>(.*?)</\1>', row)
                            for k, v in fields:
                                # Print interesting fields
                                if k in ['HNAMEC', 'HBED', 'ORDOCNM', 'ORDIAG', 'OP_DATE', 'HKID']:
                                    print(f"  {k}: {v}")
                    else:
                        print("[-] Could not identify row tag.")
                else:
                    print("[-] NewDataSet empty or not found.")
            else:
                print("[-] No DataSet found in response.")
                print("Preview:")
                print(text[:500])

        except Exception as e:
            print(f"[-] Parse error: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    client = HISPreAnesthesiaClient()
    client.get_data()
