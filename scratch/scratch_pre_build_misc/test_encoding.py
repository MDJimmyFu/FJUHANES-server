import requests
import re
import html

url = 'http://10.10.246.73/ReportOrder/OpoQ0R1Form.aspx?sUSERID=A03772&patientId=003003641A&sOPDSection=&sOPDCaseNo='
try:
    r = requests.get(url, timeout=10)
    print(f"Encoding: {r.encoding}")
    print(f"Apparent Encoding: {r.apparent_encoding}")
    
    # Try with both encodings
    for enc in ['utf-8', 'big5', 'cp950']:
        try:
            text = r.content.decode(enc)
            print(f"[{enc}] Success. Length: {len(text)}")
            if "正式" in text:
                print(f"[{enc}] Found '正式'")
            if "68" in text:
                print(f"[{enc}] Found '68'")
                
            # Test regex
            text_clean = re.sub(r'\s+', ' ', text)
            rows = re.findall(r'<tr class="(Grid|GridAlt|GridSelected)".*?>(.*?)</tr>', text_clean)
            print(f"[{enc}] Found {len(rows)} rows with Grid class")
            
            for cls, row in rows:
                if '68' in row:
                    print(f"[{enc}] Found row with 68")
                    cols = re.findall(r'<td.*?>(.*?)</td>', row)
                    if len(cols) >= 4:
                        status = re.sub(r'<.*?>|&nbsp;', '', cols[3]).strip()
                        print(f"[{enc}] Status col content: {status}")

        except Exception as ex:
             print(f"[{enc}] Failed: {ex}")
             
except Exception as e:
    print(f"Error: {e}")
