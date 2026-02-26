from his_client_final import HISClient
import sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

c = HISClient()
targets = ["003380272B", "003617359I", "003600459I", "003380272B"]

for t in targets:
    print(f"[*] Checking {t} for any EMG notes...")
    # Find EMG caseno
    query = f"SELECT HCASENO FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{t}' AND HINCURSVCL = 'EMG'"
    res = c._execute_sql_raw(query)
    if res and '<NewDataSet>' in res:
        rows = c._parse_sql_rows_raw(res)
        for r in rows:
            cn = r['HCASENO']
            print(f"  [+] Case {cn}")
            # Check ADM note
            q_adm = f"SELECT count(*) as cnt FROM COMMON.PAT_EMG_NOTE_ADM WHERE ECASENO = '{cn}'"
            r_adm = c._execute_sql_raw(q_adm)
            if r_adm and '<NewDataSet>' in r_adm:
                cnt = c._parse_sql_rows_raw(r_adm)[0].get('CNT', 0)
                if int(cnt) > 0: print(f"    - PAT_EMG_NOTE_ADM: {cnt} rows")

            # Check POMR note
            q_pomr = f"SELECT count(*) as cnt FROM COMMON.PAT_EMG_NOTE_POMR WHERE ECASENO = '{cn}'"
            r_pomr = c._execute_sql_raw(q_pomr)
            if r_pomr and '<NewDataSet>' in r_pomr:
                cnt = c._parse_sql_rows_raw(r_pomr)[0].get('CNT', 0)
                if int(cnt) > 0: print(f"    - PAT_EMG_NOTE_POMR: {cnt} rows")
