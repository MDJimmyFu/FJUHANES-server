import re
import html

def parse_lab_reports():
    with open('lab_report_page.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clean up whitespace
    content = re.sub(r'\s+', ' ', content)
    
    # Find rows
    rows = re.findall(r'<tr class="(Grid|GridAlt|GridSelected)".*?>(.*?)</tr>', content)
    
    results = []
    for cls, row_content in rows:
        cols = re.findall(r'<td.*?>(.*?)</td>', row_content)
        if len(cols) >= 8:
            name = re.sub(r'<.*?>|&nbsp;', '', cols[1]).strip()
            sample = re.sub(r'<.*?>|&nbsp;', '', cols[2]).strip()
            status = re.sub(r'<.*?>|&nbsp;', '', cols[3]).strip()
            order_ap_no = re.sub(r'<.*?>|&nbsp;', '', cols[7]).strip()
            
            onclick_match = re.search(r"onclick=\"(.*?)\"", f'<tr class="{cls}" {row_content}>')
            onclick = onclick_match.group(1) if onclick_match else ""
            url_match = re.search(r"load_page\('(.*?)'\)", onclick)
            url = url_match.group(1) if url_match else ""
            
            results.append({
                "name": name,
                "sample": sample,
                "status": status,
                "order_ap_no": order_ap_no,
                "url": url
            })
            
    # Match 68 or Formal Report
    # Note: encoding issues might mean "正式報告" looks different, but let's try
    official_reports = [r for r in results if '68' in r['status']]
    
    print(f"Total rows found: {len(results)}")
    print(f"68 reports found: {len(official_reports)}")
    
    for r in results:
        # Check if it contains "正式" or the user's specific "68"
        if '68' in r['status'] or '正式' in r['status']:
             print(f"[*] {r['status']} | {r['name']} | {r['order_ap_no']} | {r['url']}")
        # Fallback print one row to check encoding
        elif len(results) > 0 and r == results[0]:
             print(f"[Sample Row] Status: {r['status']} | Name: {r['name']}")

if __name__ == "__main__":
    parse_lab_reports()
