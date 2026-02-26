import requests

AUTH_URL = "http://10.10.246.80/Ipo/HISLogin/CheckUserByID"

def validate_login(username, password):
    """
    Validates credentials against the hospital HIS Login API.
    Returns the user data dictionary on success, None on failure.
    """
    try:
        # The API expects form data: signOnID and signOnPassword
        resp = requests.post(AUTH_URL, data={
            'signOnID': username.upper(),
            'signOnPassword': password
        }, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            # Success response typically includes SignOnID, UserName, etc.
            if data and data.get('SignOnID'):
                return data
            else:
                print(f"[-] Login failed: {data}")
        else:
            print(f"[-] Auth server returned status {resp.status_code}")
            
        return None
    except Exception as e:
        print(f"[-] Auth Error: {e}")
        return None
