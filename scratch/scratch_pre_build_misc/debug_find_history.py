from find_table_owner import SchemaAngel
import re, sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

angel = SchemaAngel()

def parse_rows(text):
    rows = re.findall(r'<DRMODIFY[^>]*>(.*?)</DRMODIFY>', text, re.DOTALL)
    results = []
    for row in rows:
        fields = re.findall(r'<(\w+)>(.*?)</\1>', row)
        results.append({k: v for k, v in fields})
    return results

hhistnum = "003363078D"

# Try 1: Direct query ORRANER with subquery on HCASENO
print("=== 1. Try ORRANER with HCASENO from PAT_ADM_CASE ===")
# First get HCASENOs for this patient
q = f"SELECT HCASENO FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhistnum}' AND ROWNUM <= 20"
res = angel.execute_sql(q)
if res and "NewDataSet" in res:
    rows = parse_rows(res)
    casenums = [r.get('HCASENO','') for r in rows]
    print(f"  Found {len(casenums)} case numbers: {casenums[:10]}")
    
    # Now try ORRANER with these case numbers
    if casenums:
        for cn in casenums[:5]:
            q2 = f"SELECT ORDSEQ, HCASENO, ANENM, ANEASA FROM OPDUSR.ORRANER WHERE HCASENO = '{cn}'"
            res2 = angel.execute_sql(q2)
            if res2 and "NewDataSet" in res2:
                rows2 = parse_rows(res2)
                if rows2:
                    print(f"  [+] ORRANER for HCASENO={cn}: {len(rows2)} rows")
                    for r in rows2:
                        print(f"    ORDSEQ={r.get('ORDSEQ','')} ANE={r.get('ANENM','')} ASA={r.get('ANEASA','')}")
            else:
                print(f"  [-] ORRANER for HCASENO={cn}: no data")
else:
    print("  No case numbers found in PAT_ADM_CASE")
    
    # Alternative: try the ORRANER with HHISNUM through ORDSEQ table
    print("\n  Trying alternative: Find ORDSEQ via search...")
