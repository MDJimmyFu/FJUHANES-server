import ast
import re

with open("full_c430_dump.txt", "r", encoding='utf-8', errors='replace') as f:
    text = f.read()

# Look for patterns like {'...'}
dicts = re.findall(r"\{'[^{}]+\}", text)

for d_str in dicts:
    try:
        # Simplify slightly to avoid ast errors with some characters
        d = ast.literal_eval(d_str.replace("?", "?"))
        
        # Check common time fields
        b_keys = ["BEGINDATETIME", "ANEBGNDTTM", "ORSDTTM"]
        e_keys = ["ENDDATETIME", "ANEENDDTTM", "OREDTTM"]
        
        for bk, ek in zip(b_keys, e_keys):
            if bk in d and ek in d:
                bv = d[bk]
                ev = d[ek]
                if bv and ev and bv != ev and "9999" not in ev and "0001" not in bv:
                    print(f"Found diff in {bk}/{ek}: {bv} -> {ev}")
                    print(f"Record: {d.get('ORDSEQ', 'no-id')} - {d.get('HHISNUM', 'no-id')}")
    except:
        pass
