import re
import json

html = """
<center>
<h3>本次就診會診資料</h3><table><tr><th>被會診醫師</th><th>會診發出時間</th><th>會診醫師</th><th>狀態</th><th>功能</th><tr><td>張書豪 ( 骨科 )</td><td>2026-02-19 18:19:08</td><td>陳永昌</td><td>已回覆</td><td> [ <a href='consult_form_view.php?ordseq=E46807673OR0028&HCASENO=46807673'>查詢</a> ]</td></table></center>
"""

base_url = "http://10.10.242.59/consult_query/"
parts = html.split('<tr>')
consultations = []
for part in parts:
    cols = re.findall(r"<td>(.*?)</td>", part, re.DOTALL)
    if len(cols) >= 5:
        # Extract link from last column
        link_match = re.search(r"href='(.*?)'", cols[4])
        report_link = f"{base_url}{link_match.group(1)}" if link_match else ""
        consultations.append({
            "target_dr": cols[0].strip(),
            "request_time": cols[1].strip(),
            "request_dr": cols[2].strip(),
            "status": cols[3].strip(),
            "url": report_link
        })

print(json.dumps(consultations, indent=2, ensure_ascii=False))
