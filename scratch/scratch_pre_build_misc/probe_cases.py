from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
caseno_1 = "46807110" # Duplicate issue
caseno_2 = "46402990" # Ghost consult issue

print(f"[*] Probing {caseno_1} (EMG/OPD Shared Case)")
q1 = f"SELECT * FROM OPDUSR.OPDDIAG WHERE OPDCASENO = '{caseno_1}'"
res1 = c._execute_sql_raw(q1)
rows1 = c._parse_sql_rows_raw(res1)
for r in rows1:
    print(f"  OPDDIAG: {r.get('DXNMC')} | {r.get('DXNME')} | {r.get('PROCNMC')}")

q1_adm = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HCASENO = '{caseno_1}'"
res1_adm = c._execute_sql_raw(q1_adm)
rows1_adm = c._parse_sql_rows_raw(res1_adm)
for r in rows1_adm:
    print(f"  PAT_ADM_CASE: {r.get('HINCURSVCL')} | {r.get('HINDIAG')} | {r.get('HVDOCNM')}")

print(f"\n[*] Probing {caseno_2} (Ghost Consult)")
q2 = f"SELECT * FROM OPDUSR.OPDREFM WHERE OPDCASENO = '{caseno_2}'"
res2 = c._execute_sql_raw(q2)
rows2 = c._parse_sql_rows_raw(res2)
for r in rows2:
    print(f"  OPDREFM: {r.get('OPDSECTION')} | {r.get('OPDDRNMC')} | {r.get('REFINREASON')} | {r.get('REFINSTATUS')}")

print("\n[*] Checking for other Consultation tables...")
# Maybe some consults are in OPDREFS?
q2_refs = f"SELECT * FROM OPDUSR.OPDREFS WHERE OPDCASENO = '{caseno_2}'"
res2_refs = c._execute_sql_raw(q2_refs)
rows2_refs = c._parse_sql_rows_raw(res2_refs)
for r in rows2_refs:
    print(f"  OPDREFS: {r.get('OPDSECTION')} | {r.get('OPDDRNMC')} | {r.get('REFINREASON')}")
