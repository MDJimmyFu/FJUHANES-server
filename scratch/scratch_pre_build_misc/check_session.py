import requests
import json

login_url = "http://auth.fjcuh.org.tw/UOF/cds/ws/SSOWS.asmx/VerifyUser"
api_url = "http://10.10.246.90:8800/HISOrmC250Facade"

def check_session():
    s = requests.Session()
    
    print(f"[-] Logging in to {login_url}...")
    payload = {
        "cry1": "A03772",
        "cry2": "Qwer12345"
    }
    
    try:
        resp = s.post(login_url, data=payload)
        print(f"Login Status: {resp.status_code}")
        print(f"Login Response: {resp.text}")
        print("Session Cookies after login:")
        for c in s.cookies:
            print(f"  {c.name} = {c.value}")
            
        print("-" * 40)
        
        # Now try to hit the API with a dummy binary body
        # We want to see if we get 401 (Auth needed) or 500 (Auth OK, Body bad)
        print(f"[-] Sending dummy request to {api_url}...")
        
        dummy_body = b"\x00\x00\x00\x00" # Just garbage
        headers = {
            "Content-Type": "application/octet-stream",
            "X-Compress": "yes" 
        }
        
        resp_api = s.post(api_url, data=dummy_body, headers=headers)
        print(f"API Response Status: {resp_api.status_code}")
        print(f"API Response Headers: {json.dumps(dict(resp_api.headers), indent=2)}")
        
        # Check if we got the Serialization Exception (meaning Auth passed)
        if resp_api.status_code == 200: # .NET Remoting often returns 200 for app exceptions
             print("API returned 200. This implies Network/Transport Auth (if any) succeeded.")
             # Check body for exception
             try:
                 print("API Body Preview: " + repr(resp_api.content[:100]))
             except:
                 pass
        elif resp_api.status_code in [401, 403]:
             print("API returned 401/403. Authentication is MISSING.")
        else:
             print(f"API returned {resp_api.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_session()
