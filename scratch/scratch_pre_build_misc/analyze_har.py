import json
import urllib.parse
import sys
import os

def analyze_har(file_path):
    print(f"Analyzing {file_path}...")
    
    if not os.path.exists(file_path):
        print("File not found.")
        return

    with open(file_path, 'r', encoding='utf-8-sig') as f: # utf-8-sig for BOM if present
        try:
            har_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

    entries = har_data.get('log', {}).get('entries', [])
    print(f"Found {len(entries)} entries.")

    login_candidates = []
    api_candidates = []
    
    for entry in entries:
        request = entry.get('request', {})
        url = request.get('url', '')
        method = request.get('method', '')
        post_data = request.get('postData', {})
        text = post_data.get('text', '')
        
        # Heuristic for Login: POST method + "password" in body or typical auth keywords in URL
        if method == 'POST' and ('login' in url.lower() or 'auth' in url.lower() or (text and 'password' in text.lower())):
             login_candidates.append({
                 'url': url,
                 'method': method,
                 'headers': {h['name']: h['value'] for h in request.get('headers', [])},
                 'payload': text
             })

        # Heuristic for Patient Data: "patient" in URL
        if 'patient' in url.lower() or 'search' in url.lower():
             api_candidates.append({
                 'url': url,
                 'method': method,
                 'payload': text if method == 'POST' else 'N/A (GET)'
             })

    print("\n--- POSSIBLE LOGIN ENDPOINTS ---")
    for i, c in enumerate(login_candidates):
        print(f"[{i+1}] {c['method']} {c['url']}")
        print(f"    Payload: {c['payload'][:200]}...") # Truncate likely sensitive/long data
        
    print("\n--- POSSIBLE PATIENT DATA ENDPOINTS ---")
    for i, c in enumerate(api_candidates):
        print(f"[{i+1}] {c['method']} {c['url']}")
        print(f"    Payload: {c['payload'][:200]}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_har.py <path_to_har_file>")
    else:
        analyze_har(sys.argv[1])
