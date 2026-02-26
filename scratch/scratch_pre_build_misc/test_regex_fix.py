import re
import html

def test_regex():
    with open('lab_report_page.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(r'\s+', ' ', content)
    rows = re.findall(r'<tr([^>]*class="(?:Grid|GridAlt|GridSelected)"[^>]*)>(.*?)</tr>', content)
    
    print(f"Found {len(rows)} rows")
    for attrs, row_content in rows:
        url_match = re.search(r"load_page\('(.*?)'\)", attrs)
        detail_url = url_match.group(1) if url_match else ""
        
        status_match = re.findall(r'<td.*?>(.*?)</td>', row_content)
        if len(status_match) >= 4:
            status = re.sub(r'<.*?>|&nbsp;', '', status_match[3]).strip()
            name = re.sub(r'<.*?>|&nbsp;', '', status_match[1]).strip()
            if '68' in status:
                print(f"[*] {status} | {name} | URL: {detail_url}")

if __name__ == "__main__":
    test_regex()
