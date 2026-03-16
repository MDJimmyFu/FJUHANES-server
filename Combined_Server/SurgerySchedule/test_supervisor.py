import sys
import os
sys.path.append(os.getcwd())
import re
from his_client_final import HISClient

def test_query():
    client = HISClient()
    hhistnum = '003013132J' # Or any known MRN with a supervisor
    
    # 1. ADM / EMG casenos
    q1 = f"SELECT HCASENO FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhistnum}'"
    res1 = client._execute_sql(q1, 'A03772')
    
    # 2. OPD casenos
    q2 = f"SELECT OPDCASENO FROM OPDUSR.OPDDIAG WHERE HHISNUM = '{hhistnum}'"
    res2 = client._execute_sql(q2, 'A03772')
    
    casenums = set()
    if res1 and '<NewDataSet>' in res1:
        match1 = re.findall(r'<HCASENO>([^<]*)</HCASENO>', res1)
        casenums.update(match1)
    
    if res2 and '<NewDataSet>' in res2:
        match2 = re.findall(r'<OPDCASENO>([^<]*)</OPDCASENO>', res2)
        casenums.update(match2)
        
    found_ane = []
    # Test ORRANER for each
    for cn in casenums:
        if not cn: continue
        q3 = f"SELECT * FROM OPDUSR.ORRANER WHERE HCASENO = '{cn}' AND CANCELYN = 'N'"
        res3 = client._execute_sql(q3, 'A03772')
        if res3 and '<NewDataSet>' in res3:
            rows = re.findall(r'<DRMODIFY[^>]*>(.*?)</DRMODIFY>', res3, re.DOTALL)
            for row in rows:
                ane = {}
                fields = re.findall(r'<(\w+)>(.*?)</\1>', row)
                for k, v in fields: ane[k] = v
                found_ane.append(ane)
                
    for ane in found_ane:
        print(f"Date: {ane.get('ANEBGNDTTM')}, Method: {ane.get('ANENM')}")
        # Print all keys that might relate to supervisor/doctor
        for k, v in ane.items():
            if 'DOC' in k or 'SUP' in k or 'NMC' in k or 'NAME' in k or 'DIR' in k:
                print(f"  {k}: {v}")

if __name__ == '__main__':
    test_query()
