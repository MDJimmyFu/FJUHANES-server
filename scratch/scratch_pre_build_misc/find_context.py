import os
import glob

def find_context(file_path, patterns):
    print(f"--- {os.path.basename(file_path)} ---")
    try:
        with open(file_path, "rb") as f:
            blob = f.read()
            
        for enc in ['utf-16', 'utf-16-le', 'utf-16-be', 'utf-8', 'ascii']:
            try:
                content = blob.decode(enc)
                for p in patterns:
                    start = 0
                    while True:
                        idx = content.find(p, start)
                        if idx == -1:
                            break
                        print(f"[MATCH {p}] ... {content[max(0, idx-100):min(len(content), idx+100)]} ...")
                        start = idx + 1
                return
            except:
                continue
    except Exception as e:
        print(f"Error: {e}")

find_context("extracted_0218_78da_40.xml", ["342", "11.2", "1.01", "139", "105"])
