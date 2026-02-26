import requests
import zlib
import datetime
import re
import os

def fetch_today_surgery():
    base_payload_file = "c250_payload_1.bin"
    url = "http://10.10.246.90:8800/HISOrmC250Facade"
    
    # 1. Read base payload
    with open(base_payload_file, "rb") as f:
        compressed_data = f.read()
        
    # 2. Decompress
    try:
        decompressed_data = zlib.decompress(compressed_data)
    except Exception as e:
        print(f"Error decompressing base payload: {e}")
        return

    # 3. Patch Date
    # Find yesterday's date (from pcap) and replace with today
    # Pcap date: 20260211
    target_date_bytes = b"20260211"
    
    today = datetime.datetime.now()
    today_str = today.strftime("%Y%m%d")
    new_date_bytes = today_str.encode('ascii')
    
    if target_date_bytes not in decompressed_data:
        print("Error: Could not find target date in payload to patch.")
        return
        
    print(f"Patching payload: {target_date_bytes} -> {new_date_bytes}")
    patched_data = decompressed_data.replace(target_date_bytes, new_date_bytes)
    
    # 4. Re-compress
    # Use standard zlib compression
    new_compressed_data = zlib.compress(patched_data)
    
    # 5. Send Request
    headers = {
        "Content-Type": "application/octet-stream",
        "X-Compress": "yes",
        "User-Agent": "Mozilla/4.0+(compatible; MSIE 6.0; Windows 6.2.9200.0; MS .NET Remoting; MS .NET CLR 2.0.50727.9164 )",
        "Expect": "100-continue",
        "Host": "10.10.246.90:8800",
        "Connection": "Keep-Alive"
    }

    print(f"Sending request for {today_str}...")
    try:
        response = requests.post(url, data=new_compressed_data, headers=headers)
        print(f"Status: {response.status_code}, Size: {len(response.content)}")
        
        if response.status_code == 200:
            # 6. Parse Response
            parse_surgery_response(response.content)
        else:
            print("Request failed.")

    except Exception as e:
        print(f"Request Error: {e}")

def parse_surgery_response(content):
    try:
        # Decompress response
        decompressed = zlib.decompress(content)
        text = decompressed.decode('utf-8', errors='ignore')
        
        # Determine if we have data
        # Look for "diffgr:diffgram" which contains the DataSet data
        if "diffgr:diffgram" in text:
            print("Found DataSet in response.")
            # Debug: Print first 2000 chars of diffgram to see structure
            d_start = text.find("<diffgr:diffgram")
            if d_start != -1:
                print("DiffGram Preview:")
                print(text[d_start:d_start+2000])

        
        # Simple extraction using regex for key fields
        # The structure usually has sequential XML tags.
        # We look for <OPSTA>...</OPSTA>, <TIME>...</TIME>
        
        # Let's try to extract rows.
        # <Table1 diffgr:id="Table11" msdata:rowOrder="0">
        #   <TIME>0830</TIME>
        #   <OPSTA>...</OPSTA>
        #   ...
        # </Table1>
        
        
        # Regex to find ORDOP_OPSTA blocks
        rows = re.findall(r'<ORDOP_OPSTA[^>]*>(.*?)</ORDOP_OPSTA>', text, re.DOTALL)
        print(f"Found {len(rows)} surgery entries.")
        
        print(f"{'Room':<5} | {'Bed':<10} | {'Doctor':<10} | {'Patient':<10} | {'Procedure'}")
        print("-" * 80)
        
        for row in rows:
            room = re.search(r'<OROPROOM>(.*?)</OROPROOM>', row)
            bed = re.search(r'<HBED>(.*?)</HBED>', row)
            doctor = re.search(r'<ORDOCNM>(.*?)</ORDOCNM>', row)
            patient = re.search(r'<HNAMEC>(.*?)</HNAMEC>', row)
            procedure = re.search(r'<ORDPROCED>(.*?)</ORDPROCED>', row)
            
            room_val = room.group(1) if room else "?"
            bed_val = bed.group(1) if bed else "?"
            doctor_val = doctor.group(1) if doctor else "?"
            patient_val = patient.group(1) if patient else "?"
            proc_val = procedure.group(1) if procedure else "?"
            
            print(f"{room_val:<5} | {bed_val:<10} | {doctor_val:<10} | {patient_val:<10} | {proc_val}")
            
    except Exception as e:
        print(f"Error parsing response: {e}")

if __name__ == "__main__":
    fetch_today_surgery()
