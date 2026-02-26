import requests
import sys

url = 'http://10.10.246.73/ReportOrder/OpoQ0R1Form.aspx?sUSERID=A03772&patientId=003003641A&sOPDSection=&sOPDCaseNo='
try:
    r = requests.get(url, timeout=10)
    html = r.text
    with open('lab_report_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Downloaded {len(html)} bytes.")
    
    # Check for "68" or "正式報告"
    if "68" in html:
        print("Found '68' in HTML.")
    if "正式報告" in html:
        print("Found '正式報告' in HTML.")
        
except Exception as e:
    print(f"Error: {e}")
