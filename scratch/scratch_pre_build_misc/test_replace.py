import zlib
import re

def test_replace():
    with open('c:\\Users\\A03772\\.gemini\\antigravity\\Combined_Server\\SurgerySchedule\\c250_payload_1.bin', 'rb') as f:
        data = zlib.decompress(f.read())
        
    start_date = b'20260215'
    end_date = b'20260216'
    
    patched = re.sub(b"(BGOPDATE.{1,30}?)20260211", b"\\g<1>" + start_date, data, flags=re.DOTALL)
    patched = re.sub(b"(ENDOPDATE.{1,30}?)20260211", b"\\g<1>" + end_date, patched, flags=re.DOTALL)
    patched = patched.replace(b"20260211", start_date)
    
    print("Success! Length changed?", len(patched) != len(data))
    
    # Check outputs
    for date in [start_date, end_date]:
        idx = patched.find(date)
        while idx != -1:
            print(f"Found {date}:", patched[max(0, idx-15):min(len(patched), idx+15)])
            idx = patched.find(date, idx + 1)

if __name__ == '__main__':
    test_replace()
