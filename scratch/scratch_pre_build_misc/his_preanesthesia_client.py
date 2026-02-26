import requests
import zlib
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

    def get_data(self, ordseq, hhistnum):
        """
        Fetches pre-anesthesia data for the given ORDSEQ and HHISTNUM.
        """
        print(f"[*] Fetching pre-anesthesia data for ORDSEQ={ordseq}, HHISTNUM={hhistnum}...")
        
        # 1. Prepare Payload
        try:
            with open(self.payload_template_path, "rb") as f:
                compressed_template = f.read()
            
            decompressed = zlib.decompress(compressed_template)
            
            # Values found in the template (from pcap analysis)
            template_hhistnum = b"003356125A"
            template_ordseq = b"A75176778OR0001"
            
            # Replace HHISTNUM
            if template_hhistnum not in decompressed:
                print("[-] Error: Template HHISTNUM not found.")
                return None
            patched_payload = decompressed.replace(template_hhistnum, hhistnum.encode('ascii'))
            
            # Replace ORDSEQ
            if template_ordseq not in patched_payload:
                print("[-] Error: Template ORDSEQ not found.")
                return None
            patched_payload = patched_payload.replace(template_ordseq, ordseq.encode('ascii'))
            
            final_payload = zlib.compress(patched_payload)
            
        except Exception as e:
            print(f"[-] Payload preparation error: {e}")
            return None

        # 2. Send Request
        try:
            response = requests.post(self.url, data=final_payload, headers=self.headers)
            response.raise_for_status()
            
            return self._parse_response(response.content)
            
        except requests.exceptions.RequestException as e:
            print(f"[-] Network error: {e}")
            return None

    def _parse_response(self, content):
        try:
            decompressed = zlib.decompress(content)
            text = decompressed.decode('utf-8', errors='replace')
            
            if "diffgr:diffgram" in text:
                print("[+] Found DataSet in response. Extracting data...")
                
                # Check for specific tables we expect
                # Based on previous generic dump, might be VITALSIGN, or other pre-anes info
                # Let's extract all key-value pairs from the first row of whatever table is there.
                
                # Find first table entry
                match = re.search(r'<NewDataSet>(.*?)</NewDataSet>', text, re.DOTALL)
                if match:
                    inner = match.group(1)
                    # Find all unique tags that look like table rows
                    # Regex to find tags inside NewDataSet
                    # A simple way is to find all <TagName ... diffgr:id="...">
                    
                    row_tags = set(re.findall(r'<(\w+)\s+diffgr:id', inner))
                    
                    full_data = {}
                    
                    if row_tags:
                        print(f"[+] Found Tables: {', '.join(row_tags)}")
                        
                        for tag in row_tags:
                            rows = re.findall(f'<{tag}[^>]*>(.*?)</{tag}>', text, re.DOTALL)
                            table_data = []
                            for row in rows:
                                fields = re.findall(r'<(\w+)>(.*?)</\1>', row)
                                table_data.append({k: v for k, v in fields})
                            full_data[tag] = table_data
                            
                        return full_data
                    else:
                        print("[-] No table rows found in DataSet.")
                        return {}
                else:
                     print("[-] Empty DataSet.")
                     return []
            else:
                print("[-] No diffgram found in response.")
                return []
                
        except Exception as e:
            print(f"[-] Parse error: {e}")
            return None

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    client = HISPreAnesthesiaClient()
    
    # Test with the first valid entry found identified earlier
    # ORDSEQ           | HHISTNUM     | Patient    | Procedure
    # A75176797OR0014  | 003158375C   | 潘永銘        | Stomach Laparoscopic gastrostomy
    
    test_ordseq = "A75176797OR0014"
    test_hhistnum = "003158375C"
    
    data = client.get_data(test_ordseq, test_hhistnum)
    
    if data:
        print(f"\n[+] Retrieved data from {len(data)} tables.")
        for table_name, records in data.items():
            print(f"\n=== Table: {table_name} ({len(records)} records) ===")
            if records:
                # Print first record as sample
                print("First Record Sample:")
                for k, v in list(records[0].items())[:10]:
                     print(f"  {k}: {v}")
    else:
        print("[-] No data found.")
