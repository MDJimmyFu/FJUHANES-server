from his_client_final import HISClient
import sys
import os

def export_full_data(target_caseno):
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    client = HISClient()
    print(f"[*] Searching for Case No: {target_caseno}...")
    
    # Check yesterday (20260211) as known location
    surgeries = client.get_surgery_list("20260211")
    found = next((s for s in surgeries if target_caseno in s['ordseq']), None)
    
    output_path = r"c:\Users\A03772\.gemini\antigravity\brain\576fe700-d230-423a-904e-c534c67e7f4b\anesthesia_charging_75176750_full.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Full Data Dump: Case {target_caseno}\n\n")
        
        if found:
            f.write(f"**Patient**: {found['patient']}\n")
            f.write(f"**ORDSEQ**: {found['ordseq']}\n")
            f.write(f"**HHISTNUM**: {found['hhistnum']}\n\n")
            
            print(f"[*] Fetching Q050 Data...")
            charging = client.get_anesthesia_charging_data(found['ordseq'], found['hhistnum'])
            
            if charging:
                 f.write(f"Total Tables: {len(charging)}\n\n")
                 
                 for table_name, records in charging.items():
                     f.write(f"## Table: {table_name} ({len(records)} records)\n\n")
                     
                     if not records:
                         f.write("*No records.*\n\n")
                         continue

                     # Collect all unique keys for header
                     all_keys = set()
                     for r in records:
                         all_keys.update(r.keys())
                     sorted_keys = sorted(list(all_keys))
                     
                     # Write as Markdown Table (Transposed if too many columns? No, standard table is better for many rows)
                     # If many columns, maybe list view is better?
                     # Let's do List view per record to ensure nothing is cut off and long values wrap.
                     
                     for i, r in enumerate(records):
                         f.write(f"### Record {i+1}\n")
                         f.write("| Field | Value |\n")
                         f.write("| :--- | :--- |\n")
                         for k in sorted_keys:
                             val = r.get(k, "")
                             f.write(f"| {k} | {val} |\n")
                         f.write("\n")
                         
            else:
                 f.write("No charging data found returned from API.\n")
        else:
            f.write("Case not found in surgery list.\n")
            
    print(f"[+] Export complete to {output_path}")

if __name__ == "__main__":
    export_full_data("75176750")
