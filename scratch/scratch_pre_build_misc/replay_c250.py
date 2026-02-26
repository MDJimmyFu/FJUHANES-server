import requests
import json
import base64

har_path = r"C:\Users\A03772\.gemini\antigravity\scratch\traffic.har"
url = "http://10.10.246.90:8800/HISOrmC250Facade"

def replay_request():
    print(f"Loading HAR: {har_path}")
    try:
        with open(har_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    entries = data['log']['entries']
    target_entry = None
    for entry in entries:
        if "HISOrmC250Facade" in entry['request']['url']:
            target_entry = entry
            break
            
    if not target_entry:
        print("Request not found in HAR.")
        return

    req = target_entry['request']
    print(f"Found Request: {req['url']}")
    
    # Construct Headers
    headers = {}
    for h in req['headers']:
        # Skip some headers that requests will add automatically or might cause issues
        if h['name'].lower() not in ['content-length', 'host', 'connection']:
            headers[h['name']] = h['value']
            
    # Force correct content type for binary
    headers['Content-Type'] = 'application/octet-stream'
    
    # Extract Body (Best Effort)
    post_data = req.get('postData', {})
    text = post_data.get('text', '')
    
    # Try to convert text back to bytes
    # Since we know it has replacement chars, we have to encode it back
    # The most likely encoding for the "text" representation of binary in HAR is usually latin1 or utf-8
    # But \ufffd means it was already lost. We will encode as utf-8 which preserves the replacement char
    # This effectively sends "garbage" where the original byte was, but keeps the structure.
    try:
        body = text.encode('utf-8')
    except Exception as e:
        print(f"Error encoding body: {e}")
        return

    print(f"Sending Request...")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Body Length: {len(body)} bytes")
    
    try:
        resp = requests.post(url, headers=headers, data=body)
        print(f"\nResponse Status: {resp.status_code}")
        print(f"Response Content Length: {len(resp.content)}")
        print(f"Response Headers: {resp.headers}")
        
        if resp.status_code == 200:
            print("Success! (Status 200)")
            # Try to see if it looks like the surgery list
            if b"ORDOP_OPSTA" in resp.content or len(resp.content) > 1000:
                 print("Response looks valid/large.")
            else:
                 print("Response is 200 but might be empty or error.")
                 
            with open("replay_response.bin", "wb") as f:
                f.write(resp.content)
            print("Saved response to replay_response.bin")
        else:
            print(f"Request failed with status {resp.status_code}")
            print(resp.text[:500])
            
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    replay_request()
