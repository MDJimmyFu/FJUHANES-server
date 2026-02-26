import requests
import os

def replay_surgery_list_request():
    url = "http://10.10.246.90:8800/HISOrmC250Facade"
    payload_file = "c250_payload_1.bin"
    output_file = "c250_response.bin"

    if not os.path.exists(payload_file):
        print(f"Error: {payload_file} not found.")
        return

    with open(payload_file, "rb") as f:
        payload = f.read()

    headers = {
        "Content-Type": "application/octet-stream",
        "X-Compress": "yes",
        "User-Agent": "Mozilla/4.0+(compatible; MSIE 6.0; Windows 6.2.9200.0; MS .NET Remoting; MS .NET CLR 2.0.50727.9164 )",
        "Expect": "100-continue",
        "Host": "10.10.246.90:8800",
        "Connection": "Keep-Alive"
    }

    print(f"Sending {len(payload)} bytes to {url}...")
    try:
        response = requests.post(url, data=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Content-Length: {len(response.content)}")
        print(f"Response Headers: {response.headers}")

        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Saved response to {output_file}")

        # Basic Check
        if response.status_code == 200:
             if len(response.content) > 0:
                 print("Success! Got a response.")
                 # Peek at content
                 print("First 100 bytes of response:")
                 print(response.content[:100])
                 try:
                     print("Decoded (utf-8, ignore errors):")
                     print(response.content[:500].decode('utf-8', errors='ignore'))
                 except:
                     pass
             else:
                 print("Response was 200 OK but empty.")
        else:
             print("Request failed.")

    except Exception as e:
        print(f"Error sending request: {e}")

if __name__ == "__main__":
    replay_surgery_list_request()
