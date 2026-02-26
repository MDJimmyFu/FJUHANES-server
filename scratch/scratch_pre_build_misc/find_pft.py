from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
# Try a few patients
targets = ["46807040", "46402990"] 
# I need ORDSEQ for get_pre_anesthesia_data
# I'll just look at get_visit_details -> 'cxr' which comes from get_patient_imaging_reports
# Wait, get_patient_imaging_reports is used for the main history view.
# app.py's getAneAssessCXRList uses get_pre_anesthesia_data.
# Which one is the user using?
# The user said "肺功能測試的網址..." usually in the context of the history view (legacy_schedule.html).
# In legacy_schedule.html:
# fetch(`/api/his/getVisitDetails?pVisitType=${type}&pCaseno=${caseno}`)
#    .then(data => { ... 
#       // cxr data is in data.cxr
#    })

# So I should check c.get_visit_details()

print("[*] Probing for PFT in visit details...")

found = False
for hhis in ["003617191C", "003600459I", "003380272B", "000639678C"]:
    print(f"Checking {hhis}...")
    hist = []
    try:
        hist = c.get_comprehensive_patient_history(hhis)
    except:
        continue
        
    for h in hist:
        # Check this visit
        details = c.get_visit_details(h['caseno'], h['type'])
        cxr = details.get('cxr', [])
        for item in cxr:
            name = item.get('ORDPROCED', '').upper()
            typ = item.get('PFTYPE', '').upper() # If exists
            if 'PULMONARY' in name or 'PFT' in name or 'LUNG' in name or 'PFT' in typ:
                print(f"[!] FOUND PFT Candidate in Case {h['caseno']}:")
                print(item)
                found = True
                break
        if found: break
    if found: break

if not found:
    print("[-] No PFT examples found.")
