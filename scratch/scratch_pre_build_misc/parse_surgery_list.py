import xml.etree.ElementTree as ET

resp_path = "c250_response.xml"

import re

def parse_surgery_list():
    try:
        # Read as binary 
        with open(resp_path, 'rb') as f:
            content = f.read()
            
        # Decode broadly
        text = content.decode('utf-8', errors='replace')
        
        # Regex to find surgery blocks
        # Pattern: <ORDOP_OPSTA ...> ... </ORDOP_OPSTA>
        # Note: attributes might vary, so use [^>]*
        pattern = re.compile(r"<ORDOP_OPSTA[^>]*>(.*?)</ORDOP_OPSTA>", re.DOTALL)
        
        matches = pattern.findall(text)
        print(f"Found {len(matches)} potential surgery records via Regex.")
        
        surgeries = []
        for match_content in matches:
            # Create a mini-xml for parsing
            mini_xml = f"<ORDOP_OPSTA>{match_content}</ORDOP_OPSTA>"
            try:
                elem = ET.fromstring(mini_xml)
                surgery = {}
                for child in elem:
                    surgery[child.tag] = child.text
                surgeries.append(surgery)
            except Exception as e:
                print(f"Failed to parse a record: {e}")

        if surgeries:
            print("-" * 100)
            print(f"{'Date':<12} {'Time':<10} {'Room':<10} {'Patient ID':<15} {'Operation'}")
            print("-" * 100)
            for s in surgeries:
                date = s.get('OP_DATE', '')
                time = s.get('OP_TIME', '')
                room = s.get('OROPROOM', '')
                pid = s.get('HHISTNUM', '')
                op = s.get('OPRSECT', '') 
                
                print(f"{date:<12} {time:<10} {room:<10} {pid:<15} {op}")
            print("-" * 100)
            
        else:
            print("No <ORDOP_OPSTA> elements found via Regex.")
            print("Preview of decoded text (first 2000 chars):")
            print(text[:2000])

    except Exception as e:
        print(f"Error parsing XML: {e}")

if __name__ == "__main__":
    parse_surgery_list()
