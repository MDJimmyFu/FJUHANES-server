from his_client_final import HISClient
import sys

def fetch_today():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    client = HISClient()
    print("[*] Attempting to fetch surgery list for TODAY...")
    
    surgeries = client.get_surgery_list()
    
    if surgeries:
        print(f"\n[+] Successfully retrieved {len(surgeries)} surgeries for today.")
        print(f"{'ORDSEQ':<16} | {'Patient':<10} | {'Doctor':<10} | {'Procedure'}")
        print("-" * 80)
        
        for s in surgeries[:20]: # Print first 20
            print(f"{s['ordseq']:<16} | {s['patient']:<10} | {s['doctor']:<10} | {s['procedure']}")
            
        if len(surgeries) > 20:
             print(f"... and {len(surgeries)-20} more.")
    else:
        print("[-] Failed to retrieve surgery list. Session might be expired or date invalid.")

if __name__ == "__main__":
    fetch_today()
