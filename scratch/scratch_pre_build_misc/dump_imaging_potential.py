from his_client_final import HISClient
import json, sys, datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
today = datetime.datetime.now().strftime("%Y%m%d")
surgeries = c.get_surgery_list(today)

if surgeries:
    for s in surgeries[:5]:
        hhistnum = s.get('HHISTNUM')
        ordseq = s.get('ORDSEQ')
        if hhistnum and ordseq:
            print(f"\n[*] Patient: {hhistnum} / {ordseq}")
            data = c.get_pre_anesthesia_data(ordseq, hhistnum, opdate=today)
            if data:
                if 'CXR' in data:
                    print(f"  [CXR DATA]: {data['CXR']}")
                if 'PAT_ADM_DRMEMO' in data:
                    print("  [MEMO DATA]:")
                    for m in data['PAT_ADM_DRMEMO']:
                        # Looking for report-like content in PAT_ADM_DRMEMO
                        # Note: _parse_dataset might only get small fields. 
                        # Let's check for CONTEXT or similar if I can.
                        print(f"    - Label: {m.get('LABEL')}")
                        # print(f"      Content: {m.get('CONTEXT', '')[:100]}...")
            else:
                print("  [-] No C430 data.")
else:
    print("[-] No surgeries for today.")
