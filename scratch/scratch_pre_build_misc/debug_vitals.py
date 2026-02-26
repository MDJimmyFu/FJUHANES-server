from his_client_final import HISClient
from hospital_login_tool import config

def dump_vitals(hhistnum):
    client = HISClient()
    user_id = 'A03772'
    
    print(f"--- Raw Vitals from OPDUSR.VITALSIGNUPLOAD for {hhistnum} ---")
    q = f"SELECT * FROM OPDUSR.VITALSIGNUPLOAD WHERE HHISNUM = '{hhistnum}' ORDER BY OCCURDATE DESC"
    res = client._execute_sql(q, user_id=user_id)
    
    import re
    # Extract unique event types manually from XML
    all_et = re.findall(r'<EVENT_TYPE>(.*?)</EVENT_TYPE>', res)
    event_types = sorted(list(set(all_et)))
    with open('vitals_debug_output.txt', 'w', encoding='utf-8') as f_out:
        f_out.write(f"Unique Event Types ({len(event_types)}): {event_types}\n")
        # Print one sample for each event type
        for et in event_types:
            pattern = rf'<DRMODIFY.*?>.*?<EVENT_TYPE>{re.escape(et)}</EVENT_TYPE>.*?<NVALUE1>(.*?)</NVALUE1>.*?<NVALUE2>(.*?)</NVALUE2>.*?<OCCURDATE>(.*?)</OCCURDATE>.*?</DRMODIFY>'
            match = re.search(pattern, res, re.DOTALL)
            if match:
                f_out.write(f"Latest {et}: {match.group(1)} / {match.group(2)} at {match.group(3)}\n")
    print("Done. Check vitals_debug_output.txt")
    
    print(f"\n--- Resulting Vitals from get_vitals_from_exm for {hhistnum} ---")
    vitals = client.get_vitals_from_exm(hhistnum, user_id=user_id)
    print(vitals)

if __name__ == "__main__":
    dump_vitals("003616525A")
