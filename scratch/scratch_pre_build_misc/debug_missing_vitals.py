from his_client_final import HISClient
import re

def search_vitals_deeply(hhistnum):
    client = HISClient()
    user_id = 'A03772'
    ordseq = 'A75176715OR0001'
    
    print(f"=== Deep Vitals Search for {hhistnum} / {ordseq} ===")
    
    # 0. Activate
    client.activate_patient(ordseq, hhistnum)

    # 1. Fetch C430 data
    pre_data = client.get_pre_anesthesia_data(ordseq, hhistnum)
    print(f"Pre-Anesthesia Data Tables: {pre_data.keys() if pre_data else 'None'}")
    
    if pre_data:
        for table, rows in pre_data.items():
            for i, row in enumerate(rows):
                # Search for any value that might be temp (35-40) or height/weight
                for k, v in row.items():
                    ks = str(k).upper()
                    vs = str(v).upper()
                    if any(term in ks or term in vs for term in ['WEIGHT', 'HEIGHT', 'TEMP', 'BT', 'WT', 'HT']):
                        print(f"[C430] {table} Row {i} | {k}: {v}")

    # 2. Check ALL history in VITALSIGNUPLOAD
    q1 = f"SELECT * FROM OPDUSR.VITALSIGNUPLOAD WHERE HHISNUM = '{hhistnum}' ORDER BY OCCURDATE DESC"
    res1 = client._execute_sql(q1, user_id=user_id)
    
    # Generic regex to find any tag containing 'BT', 'TEMP', 'WT', 'HT', 'WEIGHT', 'HEIGHT'
    potential_tags = re.findall(r'<([^>]*?(?:BT|TEMP|WT|HT|WEIGHT|HEIGHT)[^>]*?)>(.*?)</\1>', res1, re.I)
    if potential_tags:
        print(f"Found potential vital tags in VITALSIGNUPLOAD: {set(potential_tags[:20])}")

    # 3. Check OR_SIGN_IN specifically for this ORDSEQ
    q2 = f"SELECT * FROM CPOE.OR_SIGN_IN WHERE ORDSEQ = '{ordseq}'"
    res2 = client._execute_sql(q2, user_id=user_id)
    print(f"OR_SIGN_IN for {ordseq} has data: {'<NewDataSet>' in res2}")
    
    if '<NewDataSet>' in res2:
        vitals_match = re.findall(r'<(HEIGHT|WEIGHT|BT.*?)>(.*?)</\1>', res2)
        print(f"OR_SIGN_IN matches: {vitals_match}")

if __name__ == "__main__":
    search_vitals_deeply("003616525A")

if __name__ == "__main__":
    search_vitals_deeply("003616525A")
