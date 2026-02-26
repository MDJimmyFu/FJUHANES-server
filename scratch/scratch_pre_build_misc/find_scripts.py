import re
try:
    with open('login_response.html', 'r', encoding='utf-16le') as f:
        content = f.read()
    scripts = re.findall(r'script.*?src=\"(.*?)\"', content)
    for s in scripts:
        print(s)
except Exception as e:
    print(f"Error: {e}")
