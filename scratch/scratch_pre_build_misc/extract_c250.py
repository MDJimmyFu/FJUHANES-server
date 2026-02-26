import json
import zlib
import base64
import os

har_path = r"C:\Users\A03772\.gemini\antigravity\scratch\traffic.har"
log_path = r"C:\Users\A03772\.gemini\antigravity\scratch\c250_payload.log"

def analyze_requests():
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write(f"Loading HAR: {har_path}\n")
        try:
            with open(har_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                data = json.load(f)
        except Exception as e:
            log.write(f"Error loading JSON: {e}\n")
            return

        entries = data['log']['entries']
        target_found = False
        
        for entry in entries:
            req = entry['request']
            if "HISOrmC250Facade" in req['url']:
                log.write(f"\nFound Application Request: {req['url']}\n")
                log.write(f"Method: {req['method']}\n")
                
                post_data = req.get('postData', {})
                text = post_data.get('text', '')
                mime = post_data.get('mimeType', '')
                encoding = post_data.get('encoding', '') # Might be empty?

                log.write(f"Mime: {mime}\n")
                log.write(f"Encoding field: '{encoding}'\n")
                log.write(f"Text len: {len(text)}\n")
                
                log.write(f"First 100 chars repr: {repr(text[:100])}\n")

                if '\ufffd' in text:
                    log.write("CRITIAL: Found REPLACEMENT CHARACTER (\\ufffd). Data is corrupted/lost.\n")
                else:
                    log.write("No replacement characters found. Data might be recoverable.\n")
                    
                    # Try CP950 encoding as well since we are on a TW system
                    try:
                        raw_bytes = text.encode('cp950')
                        log.write("Encoded as cp950.\n")
                    except Exception as e:
                        log.write(f"CP950 encode failed: {e}\n")

                # Request content logic
                raw_bytes = None
                
                # 1. Try Base64 if encoding says so OR if it looks like it
                if encoding == "base64":
                    try:
                        raw_bytes = base64.b64decode(text)
                        log.write("Decoded explicit base64.\n")
                    except:
                        log.write("Failed explicit base64 decode.\n")
                
                if raw_bytes is None:
                    # 2. Try simple latin1 encoding
                    try:
                        raw_bytes = text.encode('latin1')
                        log.write("Encoded as latin1.\n")
                    except Exception as e:
                        log.write(f"Latin1 encode failed: {e}\n")
                        # Try utf-8
                        try:
                            raw_bytes = text.encode('utf-8')
                            log.write("Encoded as utf-8.\n")
                        except Exception as e2:
                            log.write(f"UTF-8 encode failed: {e2}\n")

                if raw_bytes:
                    # 3. Check for Zlib header (0x78)
                    log.write(f"First 4 bytes hex: {raw_bytes[:4].hex()}\n")

                    if len(raw_bytes) > 2 and raw_bytes[0] == 0x78:
                        try:
                            decompressed = zlib.decompress(raw_bytes)
                            log.write("\nSUCCESS: Decompressed Zlib Request Body!\n")
                            log.write("-" * 40 + "\n")
                            # Print recognizable text (ASCII range)
                            printable = "".join([chr(b) if 32 <= b <= 126 else "." for b in decompressed])
                            log.write(printable[:2000] + "\n") 
                            log.write("-" * 40 + "\n")
                            
                            with open("c250_decoded_request.bin", "wb") as f_out:
                                f_out.write(decompressed)
                            log.write("Saved to c250_decoded_request.bin\n")
                            
                            target_found = True
                            return # Stop after first successful one
                        except Exception as z_err:
                            log.write(f"Zlib decompress failed: {z_err}\n")
                    else:
                        log.write(f"Header bytes: {raw_bytes[:10].hex()} (Not Zlib 78...)\n")
                        # Save raw bytes anyway
                        with open("c250_raw.bin", "wb") as f_raw:
                            f_raw.write(raw_bytes)
                        log.write("Saved raw bytes to c250_raw.bin\n")
                else:
                     log.write("Could not convert text to bytes reasonably.\n")

if __name__ == "__main__":
    analyze_requests()
