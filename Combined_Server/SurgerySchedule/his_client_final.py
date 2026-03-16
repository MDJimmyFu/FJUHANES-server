import requests
import zlib
import datetime
import re
import os
import sys
import time
import html
from resource_utils import resource_path

class HISClient:
    def __init__(self, c250_template="SurgerySchedule/c250_payload_1.bin", c430_template="SurgerySchedule/c430_payload_0.bin", q050_template="SurgerySchedule/q050_payload_0.bin"):
        self.base_url = "http://10.10.246.90:8800"
        self.c250_template = resource_path(c250_template)
        self.c430_template = resource_path(c430_template)
        self.q050_template = resource_path(q050_template)
        self.c250_activate_template = resource_path("SurgerySchedule/c250_activate.bin")
        self.headers = {
            "Content-Type": "application/octet-stream",
            "X-Compress": "yes",
            "User-Agent": "Mozilla/4.0+(compatible; MSIE 6.0; Windows 6.2.9200.0; MS .NET Remoting; MS .NET CLR 2.0.50727.9164 )",
            "Expect": "100-continue",
            "Host": "10.10.246.90:8800",
            "Connection": "Keep-Alive"
        }

    def get_surgery_list(self, date_str=None, end_date_str=None):
        """
        Fetches the surgery list for the given date range (YYYYMMDD to YYYYMMDD).
        If end_date_str is not provided, it defaults to date_str.
        """
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y%m%d")
        if not end_date_str:
            end_date_str = date_str
            
        print(f"[*] Fetching surgery list from {date_str} to {end_date_str}...")
        
        try:
            with open(self.c250_template, "rb") as f:
                compressed_template = f.read()
            decompressed = zlib.decompress(compressed_template)
            
            target_date_bytes = date_str.encode('ascii')
            end_date_bytes = end_date_str.encode('ascii')
            
            # The template has 20260211 for BGOPDATE, ENDOPDATE, and OPDATE
            patched_payload = re.sub(b"(BGOPDATE.{1,30}?)20260211", b"\\g<1>" + target_date_bytes, decompressed, flags=re.DOTALL)
            patched_payload = re.sub(b"(ENDOPDATE.{1,30}?)20260211", b"\\g<1>" + end_date_bytes, patched_payload, flags=re.DOTALL)
            patched_payload = patched_payload.replace(b"20260211", target_date_bytes)
            
            final_payload = zlib.compress(patched_payload)
            
            response = requests.post(f"{self.base_url}/HISOrmC250Facade", data=final_payload, headers=self.headers)
            response.raise_for_status()
            
            return self._parse_surgery_list(response.content)
            
        except Exception as e:
            print(f"[-] Error fetching surgery list: {e}")
            return None

    def activate_patient(self, ordseq, hhistnum):
        """
        Activates a specific patient context in the HIS session.
        This is required to trigger the inclusion of laboratory data in C430 responses.
        """
        print(f"[*] Activating patient context for {hhistnum} / {ordseq}...")
        try:
            if not os.path.exists(self.c250_activate_template):
                print(f"[-] Activation template {self.c250_activate_template} not found.")
                return False

            with open(self.c250_activate_template, "rb") as f:
                compressed = f.read()
            decompressed = zlib.decompress(compressed)

            # Template values found in c250_activate.bin
            template_hhistnum = b"NONE_FOUND" # c250_activate doesn't seem to have hhistnum
            template_ordseq = b"A129523047"

            patched = decompressed.replace(template_hhistnum, hhistnum.encode('ascii'))
            patched = patched.replace(template_ordseq, ordseq.encode('ascii'))
            
            final_payload = zlib.compress(patched)
            response = requests.post(f"{self.base_url}/HISOrmC250Facade", data=final_payload, headers=self.headers)
            
            return response.status_code == 200
        except Exception as e:
            print(f"[-] Activation error: {e}")
            return False

    def get_pre_anesthesia_data(self, ordseq, hhistnum, opdate=None):
        """
        Fetches pre-anesthesia data for the given ORDSEQ and HHISTNUM.
        """
        # First activate to ensure lab data is included
        self.activate_patient(ordseq, hhistnum)
        
        print(f"[*] Fetching pre-anesthesia data for {ordseq} / {hhistnum} (Date: {opdate})...")
        
        try:
            with open(self.c430_template, "rb") as f:
                compressed_template = f.read()
            decompressed = zlib.decompress(compressed_template)
            
            # Template values from pcap
            template_hhistnum = b"003356125A"
            template_ordseq = b"A75176778OR0001"
            template_opdate = b"20260212"

            patched = decompressed.replace(template_hhistnum, hhistnum.encode('ascii'))
            patched = patched.replace(template_ordseq, ordseq.encode('ascii'))
            
            # Default to today's date if not provided (Critical for live data retrieval)
            actual_date = opdate if opdate else datetime.datetime.now().strftime("%Y%m%d")
            clean_date = actual_date.replace('-', '').replace('/', '')
            patched = patched.replace(template_opdate, clean_date.encode('ascii'))
            
            final_payload = zlib.compress(patched)
            response = requests.post(f"{self.base_url}/HISOrmC430Facade", data=final_payload, headers=self.headers)
            response.raise_for_status()
            
            return self._parse_dataset(response.content)
            
        except Exception as e:
            print(f"[-] Error fetching pre-anesthesia data: {e}")
            return None

    def get_anesthesia_charging_data(self, ordseq, hhistnum):
        """
        Fetches charging-related data using Q050 (AstarDataSet).
        """
        print(f"[*] Fetching anesthesia charging data for {ordseq}...")
        try:
            with open(self.q050_template, "rb") as f:
                compressed_template = f.read()
            decompressed = zlib.decompress(compressed_template)
            
            # Template values found in q050_payload_0.bin
            template_hhistnum = b"003162935D"
            template_ordseq = b"A75072943OR0001"
            
            patched_payload = decompressed.replace(template_hhistnum, hhistnum.encode('ascii'))
            patched_payload = patched_payload.replace(template_ordseq, ordseq.encode('ascii'))
            final_payload = zlib.compress(patched_payload)
            
            response = requests.post(f"{self.base_url}/HISOrmQ050Facade", data=final_payload, headers=self.headers)
            response.raise_for_status()
            
            return self._parse_dataset(response.content)
            
        except Exception as e:
            print(f"[-] Error fetching anesthesia charging data: {e}")
            return None

    def _execute_sql(self, sql_query, user_id=None):
        """
        Helper to execute SQL via EXM template with dynamic user mapping.
        """
        # Default to A03772 for legacy support or if not provided
        uid = user_id or "A03772"
        # Ensure user_id is padded to 6 chars if needed (though hospital IDs are usually 6)
        # Template uses A03772 (6 chars)
        uid_bytes = uid.upper()[:6].encode('ascii')

        template_path = resource_path("SurgerySchedule/HISExmFacade_payload_0.bin")
        if not os.path.exists(template_path): 
            print("[-] SQL Template missing.")
            return None
            
        with open(template_path, "rb") as f:
            compressed_template = f.read()
        try: decompressed = zlib.decompress(compressed_template)
        except: decompressed = compressed_template
        
        # Original SQL from template
        original_sql_bytes = b"SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'"
        
        # Construct dynamic SQL with target user ID
        # Since the template is binary, we replace the specific HISSYSCODE placeholder
        template_sql_str = "SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'XXXXXX' AND CANCELYN = 'N'"
        template_sql_bytes = template_sql_str.replace('XXXXXX', uid.upper()[:6]).encode('ascii')
        
        target_len = len(original_sql_bytes)
        if len(sql_query) > target_len:
            print(f"[-] SQL too long: {len(sql_query)} > {target_len}")
            return None
            
        padded_sql = sql_query.ljust(target_len)
        
        # Use simple replace if user_id length matches (6 chars). 
        patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
        
        final_payload = zlib.compress(patched_payload)
        try:
            resp = requests.post(f"{self.base_url}/HISExmFacade", data=final_payload, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                dec = zlib.decompress(resp.content)
                return dec.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"[-] SQL Execution Error: {e}")
        return None

    def get_lab_data(self, hhistnum, ordseq, pre_data=None):
        """
        Extracts and formats laboratory data from C430 response.
        """
        print(f"[*] Fetching lab data for {hhistnum} (ORDSEQ: {ordseq})...")
        mapping = {
            'WBC': 'WBC', 'HGB': 'HB', 'HCT': 'HCT', 'PLT': 'PLT',
            'PT': 'PT', 'APTT': 'PTT', 'INR': 'INR',
            'NA': 'Na', 'K': 'K', 'ALT': 'ALT', 'AST': 'AST',
            'CREA': 'Cre', 'BUN': 'BUN', 'BIL': 'T_BIL', 'CL': 'Cl', 'CA': 'Ca'
        }
        lab_results = {}
        
        if not pre_data and ordseq:
            pre_data = self.get_pre_anesthesia_data(ordseq, hhistnum)
            
        if pre_data and 'INSPECTION' in pre_data:
            for item in pre_data['INSPECTION']:
                title = item.get('TITLE', '').upper()
                val = item.get('SYB_VALUE', '')
                if title in mapping:
                    lab_results[mapping[title]] = val
                elif 'GLUCOSE' in title:
                    lab_results['Glucose'] = val
        
        # Also include raw tables for specific UI sections
        for table in ['INSPECTION_RPT', 'INSPECTION_EKG', 'INSPECTION_CXR']:
            if pre_data and table in pre_data:
                lab_results[table] = pre_data[table]
                
        return lab_results

    def _parse_surgery_list(self, content):
        try:
            text = zlib.decompress(content).decode('utf-8', errors='replace')
            entries = []
            rows = re.findall(r'<ORDOP_OPSTA[^>]*>(.*?)</ORDOP_OPSTA>', text, re.DOTALL)
            for row in rows:
                item = {}
                tags = re.findall(r'<(\w+)>(.*?)</\1>', row)
                for tag, value in tags:
                    item[tag] = value.strip()
                if item:
                    entries.append(item)
            return entries
        except Exception as e:
            print(f"[-] Parse error: {e}")
            return []

    def get_vitals_from_exm(self, hhistnum, ordseq=None, user_id=None, pre_data=None):
        """
        Fetches vitals from CPOE.OR_SIGN_IN (Weight/Height) and OPDUSR.VITALSIGNUPLOAD (Monitoring).
        """
        print(f"[*] Fetching accurate vitals from EXM for {hhistnum} / {ordseq}...")
        try:
            mapped = {}
            # 1. Fetch Weight/Height from CPOE.OR_SIGN_IN
            if ordseq:
                q_or = f"SELECT * FROM CPOE.OR_SIGN_IN WHERE ORDSEQ = '{ordseq}'"
            else:
                q_or = f"SELECT * FROM CPOE.OR_SIGN_IN WHERE HHISNUM = '{hhistnum}'"
            
            res_or = self._execute_sql(q_or, user_id=user_id)
            if res_or and "<NewDataSet>" in res_or:
                rows = re.findall(r'<DRMODIFY.*?>(.*?)</DRMODIFY>', res_or, re.DOTALL)
                for row in rows:
                    w = re.search(r'<WEIGHT>(.*?)</WEIGHT>', row)
                    h = re.search(r'<HEIGHT>(.*?)</HEIGHT>', row)
                    if w and w.group(1): mapped['WEIGHT'] = w.group(1)
                    if h and h.group(1): mapped['HEIGHT'] = h.group(1)
                    if 'WEIGHT' in mapped and 'HEIGHT' in mapped: break

            # 2. Fetch Monitoring Vitals from OPDUSR.VITALSIGNUPLOAD
            q_upload = f"SELECT * FROM OPDUSR.VITALSIGNUPLOAD WHERE HHISNUM = '{hhistnum}' ORDER BY OCCURDATE DESC"
            res_up = self._execute_sql(q_upload, user_id=user_id)
            if res_up and "<NewDataSet>" in res_up:
                rows = re.findall(r'<DRMODIFY.*?>(.*?)</DRMODIFY>', res_up, re.DOTALL)
                latest_vals = {}
                for row in rows:
                    etype_m = re.search(r'<EVENT_TYPE>(.*?)</EVENT_TYPE>', row)
                    nval_m = re.search(r'<NVALUE1>(.*?)</NVALUE1>', row)
                    nval2_m = re.search(r'<NVALUE2>(.*?)</NVALUE2>', row)
                    date_m = re.search(r'<OCCURDATE>(.*?)</OCCURDATE>', row)
                    
                    if etype_m and nval_m:
                        etype = etype_m.group(1).strip()
                        val = nval_m.group(1).strip()
                        val2 = nval2_m.group(1).strip() if nval2_m else ""
                        dt = date_m.group(1).strip() if date_m else ""
                        if etype not in latest_vals:
                            latest_vals[etype] = {'val': val, 'val2': val2, 'dt': dt}
            
                # Map Monitoring Vitals to Flat Structure
                if 'SPO2' in latest_vals:
                    mapped['SPO2'] = latest_vals['SPO2']['val']
                    mapped['SPO2_DTTM'] = latest_vals['SPO2']['dt']
                # BP Priority: ABP (Invasive) -> NBP (Non-invasive) -> other BP
                bp_key = None
                if 'BP.ABP' in latest_vals: bp_key = 'BP.ABP'
                elif 'BP.NBP' in latest_vals: bp_key = 'BP.NBP'
                else:
                    for k in latest_vals:
                        if k.startswith('BP.'):
                            bp_key = k
                            break
                
                if bp_key:
                    mapped['BP'] = f"{latest_vals[bp_key]['val']}/{latest_vals[bp_key]['val2']}"
                    mapped['BP_DTTM'] = latest_vals[bp_key]['dt']
                    if 'ABP' in bp_key: mapped['BP'] += " (ABP)"
                # PULSE Priority: PULSE.USUAL -> HR.ECG -> PULSE -> HR
                pulse_key = None
                for pk in ['PULSE.USUAL', 'HR.ECG', 'PULSE', 'HR']:
                    if pk in latest_vals:
                        pulse_key = pk
                        break
                if pulse_key:
                    mapped['PULSE'] = latest_vals[pulse_key]['val']
                    mapped['PULSE_DTTM'] = latest_vals[pulse_key]['dt']

                # RESP Priority: RESPIRATORY -> RR -> RESP
                resp_key = None
                for rk in ['RESPIRATORY', 'RR', 'RESP']:
                    if rk in latest_vals:
                        resp_key = rk
                        break
                if resp_key:
                    mapped['RESP'] = latest_vals[resp_key]['val']
                    mapped['RESP_DTTM'] = latest_vals[resp_key]['dt']
                if 'BT.EAR' in latest_vals:
                    mapped['BT'] = latest_vals['BT.EAR']['val']
                    mapped['BT_DTTM'] = latest_vals['BT.EAR']['dt']

                # Fallback for ALL vitals from pre_data (C430 VITALSIGN tables)
                if pre_data:
                    # Height
                    if mapped.get('HEIGHT', '0') in ['0', '', None]:
                        v = pre_data.get('VITALSIGN_HEIGHT', [])
                        if v and v[0].get('HEIGHT'): mapped['HEIGHT'] = v[0]['HEIGHT']
                    
                    # Weight
                    if mapped.get('WEIGHT', '0') in ['0', '', None]:
                        v = pre_data.get('VITALSIGN_WEIGHT', [])
                        if v and v[0].get('WEIGHT'): mapped['WEIGHT'] = v[0]['WEIGHT']
                    
                    # BT (Temperature)
                    if mapped.get('BT', '0') in ['0', '', None]:
                        v = pre_data.get('VITALSIGN_BTVALUE', [])
                        if v and v[0].get('BTVALUE'): 
                            mapped['BT'] = v[0]['BTVALUE']
                            if v[0].get('BTSITE'): mapped['BT'] = f"{mapped['BT']} ({v[0]['BTSITE']})"
                    
                    # BP
                    if mapped.get('BP', '0') in ['0', '', None]:
                        v = pre_data.get('VITALSIGN_SBPDBPVALUE', [])
                        if v and v[0].get('SBP') and v[0].get('DBP'):
                            mapped['BP'] = f"{v[0]['SBP']}/{v[0]['DBP']} (C430)"
                    
                    # PULSE
                    if mapped.get('PULSE', '0') in ['0', '', None]:
                        v = pre_data.get('VITALSIGN_PULSEVALUE', [])
                        if v and v[0].get('PULSEVALUE'): mapped['PULSE'] = v[0]['PULSEVALUE']
                    
                    # RESP
                    if mapped.get('RESP', '0') in ['0', '', None]:
                        v = pre_data.get('VITALSIGN_RESPVALUE', [])
                        if v and v[0].get('RESPVALUE'): mapped['RESP'] = v[0]['RESPVALUE']
                    
                    # SPO2
                    if mapped.get('SPO2', '0') in ['0', '', None]:
                        v = pre_data.get('VITALSIGN_SPO2', [])
                        if v and v[0].get('SPO2'): mapped['SPO2'] = v[0]['SPO2']

                # Standard Monitoring fallbacks
                if mapped.get('HEIGHT', '0') == '0' and 'HEIGHT' in latest_vals: mapped['HEIGHT'] = latest_vals['HEIGHT']['val']
                if mapped.get('WEIGHT', '0') == '0' and 'WEIGHT' in latest_vals: mapped['WEIGHT'] = latest_vals['WEIGHT']['val']
                if mapped.get('HEIGHT', '0') == '0' and 'BODY HEIGHT' in latest_vals: mapped['HEIGHT'] = latest_vals['BODY HEIGHT']['val']
                if mapped.get('WEIGHT', '0') == '0' and 'BODY WEIGHT' in latest_vals: mapped['WEIGHT'] = latest_vals['BODY WEIGHT']['val']

            return mapped
        except Exception as e:
            print(f"[-] Error in get_vitals_from_exm: {e}")
            return {}

    def get_anesthesia_history(self, hhistnum, user_id=None):
        """
        Fetches anesthesia history for a patient using HHISTNUM (病歷號).
        """
        print(f"[*] Fetching anesthesia history via SQL for {hhistnum}...")
        try:
            def parse_sql_rows(text):
                rows = re.findall(r'<DRMODIFY[^>]*>(.*?)</DRMODIFY>', text, re.DOTALL)
                results = []
                for row in rows:
                    fields = re.findall(r'<(\w+)>(.*?)</\1>', row)
                    results.append({k: v for k, v in fields})
                return results

            q1 = f"SELECT HCASENO FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhistnum}'"
            res1 = self._execute_sql(q1, user_id=user_id)
            
            q_opd = f"SELECT OPDCASENO FROM OPDUSR.OPDDIAG WHERE HHISNUM = '{hhistnum}'"
            res_opd = self._execute_sql(q_opd, user_id=user_id)
            
            casenums = set()
            if res1 and '<NewDataSet>' in res1:
                case_rows = parse_sql_rows(res1)
                casenums.update([r.get('HCASENO', '') for r in case_rows if r.get('HCASENO')])
                
            if res_opd and '<NewDataSet>' in res_opd:
                opd_rows = parse_sql_rows(res_opd)
                casenums.update([r.get('OPDCASENO', '') for r in opd_rows if r.get('OPDCASENO')])
                
            casenums = list(casenums)

            all_history = []
            for cn in casenums:
                q2 = f"SELECT * FROM OPDUSR.ORRANER WHERE HCASENO = '{cn}' AND CANCELYN = 'N'"
                res2 = self._execute_sql(q2, user_id=user_id)
                if res2 and '<NewDataSet>' in res2:
                    rows = parse_sql_rows(res2)
                    for r in rows: r['HCASENO'] = cn
                    all_history.extend(rows)
            
            if all_history:
                opd_map = {} 
                for cn in casenums:
                    q3 = f"SELECT * FROM OPDUSR.OPDORDM WHERE OPDCASENO = '{cn}' AND CANCELYN = 'N'"
                    res3 = self._execute_sql(q3, user_id=user_id)
                    if res3 and '<NewDataSet>' in res3:
                        opd_rows = parse_sql_rows(res3)
                        for r in opd_rows:
                            oseq = r.get('ORDSEQ')
                            if oseq:
                                opd_map[oseq] = {'PFNM': r.get('PFNM', ''), 'CHARGEFLAG': r.get('CHARGEFLAG', 'N')}
                
                final_history = []
                for h in all_history:
                    oseq = h.get('ORDSEQ')
                    if oseq in opd_map and opd_map[oseq]['CHARGEFLAG'] == 'Y':
                        h['ORDPROCED'] = opd_map[oseq]['PFNM']
                        final_history.append(h)
                all_history = final_history

            all_history.sort(key=lambda x: x.get('ANEBGNDTTM', ''), reverse=True)
            all_history = [h for h in all_history if h.get('COST_ID')]
            return all_history
        except Exception as e:
            print(f"[-] Error in get_anesthesia_history: {e}")
            return []

    def _execute_sql_raw(self, sql_query, user_id=None):
        return self._execute_sql(sql_query, user_id=user_id)

    def _parse_sql_rows_raw(self, text, tag="DRMODIFY"):
        if not text: return []
        rows = re.findall(f'<{tag}[^>]*>(.*?)</{tag}>', text, re.DOTALL)
        results = []
        for row in rows:
            fields = re.findall(r'<(\w+)>(.*?)</\1>', row, re.DOTALL)
            results.append({k: v for k, v in fields})
        return results

    def get_admission_history(self, hhistnum, user_id=None):
        try:
            q = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhistnum}' ORDER BY HADMDT DESC"
            res = self._execute_sql_raw(q, user_id=user_id)
            history = []
            if res and '<NewDataSet>' in res:
                rows = self._parse_sql_rows_raw(res)
                for r in rows:
                    history.append({'hcaseno': r.get('HCASENO', ''), 'admdt': r.get('HADMDT', ''), 'admtm': r.get('HADMTM', ''), 'disdt': r.get('HDISDT', ''), 'distm': r.get('HDISTM', ''), 'dept': r.get('HINCURSVCL', ''), 'ward': r.get('HNURSTA', ''), 'bed': r.get('HBED', ''), 'diagnosis': r.get('HINDIAG', ''), 'diagnosis_desc': r.get('HINDIAGDESC', ''), 'doctor': r.get('HVDOCNM', ''), 'patstat': r.get('HPATSTAT', '')})
            return history
        except Exception as e: return []

    def get_comprehensive_patient_history(self, hhistnum, user_id=None):
        try:
            adm_query = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhistnum}' ORDER BY HADMDT DESC"
            adm_res = self._execute_sql_raw(adm_query, user_id=user_id)
            adm_list = []
            if adm_res and '<NewDataSet>' in adm_res:
                rows = self._parse_sql_rows_raw(adm_res)
                for r in rows:
                    vtype = 'EMG' if r.get('HINCURSVCL') == 'EMG' else 'ADM'
                    adm_list.append({'caseno': r.get('HCASENO', ''), 'date': r.get('HADMDT', ''), 'type': vtype, 'dept': r.get('HINCURSVCL', ''), 'diagnosis': r.get('HINDIAG', ''), 'diagnosis_desc': r.get('HINDIAGDESC', ''), 'doctor': r.get('HVDOCNM', ''), 'ward_bed': f"{r.get('HNURSTA','')}-{r.get('HBED','')}" if vtype == 'ADM' else r.get('HNURSTA',''), 'dis_date': r.get('HDISDT', '')})
            opd_query = f"SELECT * FROM OPDUSR.OPDDIAG WHERE HHISNUM = '{hhistnum}' ORDER BY CREATEDATETIME DESC"
            opd_res = self._execute_sql_raw(opd_query, user_id=user_id)
            opd_visits = {}
            if opd_res and '<NewDataSet>' in opd_res:
                rows = self._parse_sql_rows_raw(opd_res)
                for r in rows:
                    cn = r.get('OPDCASENO')
                    if cn and cn not in opd_visits:
                        opd_visits[cn] = {'caseno': cn, 'date': r.get('CREATEDATETIME', '')[:8], 'type': 'OPD', 'dept': '', 'diagnosis': r.get('DXNMC', ''), 'diagnosis_desc': r.get('DXNME', ''), 'doctor': r.get('PROCNMC', ''), 'ward_bed': '', 'dis_date': ''}
            adm_casenos = {a['caseno'] for a in adm_list if a.get('caseno')}
            all_history = adm_list + [v for cn, v in opd_visits.items() if cn not in adm_casenos]
            all_history.sort(key=lambda x: x['date'], reverse=True)
            return all_history
        except Exception as e: return []

    def get_visit_details(self, caseno, vtype='ADM', user_id=None):
        try:
            med_query = f"SELECT * FROM OPDUSR.OPDORDM WHERE OPDCASENO = '{caseno}' AND ORTYPE = 'OD' AND CANCELYN = 'N'"
            med_res = self._execute_sql_raw(med_query, user_id=user_id)
            meds = []
            if med_res and '<NewDataSet>' in med_res:
                rows = self._parse_sql_rows_raw(med_res)
                for r in rows: meds.append({'name': r.get('PFNM', ''), 'dose': f"{r.get('DOSE','')} {r.get('GIVUNIT','')}", 'freq': r.get('FREQUENCY', ''), 'route': r.get('ROUTE', ''), 'memo': r.get('ORDERMEMO', '')})
            
            cons_query = f"SELECT * FROM OPDUSR.OPDREFM WHERE OPDCASENO = '{caseno}' AND CANCELYN = 'N'"
            cons_res = self._execute_sql_raw(cons_query, user_id=user_id)
            consults = []
            if cons_res and '<NewDataSet>' in cons_res:
                rows = self._parse_sql_rows_raw(cons_res)
                for r in rows:
                    status = r.get('REFINSTATUS', '')
                    reason = r.get('REFINREASON', '')
                    if status == 'I' and reason == '50': continue
                    consults.append({'date': r.get('CREATEDATETIME', ''), 'target_dept': r.get('REFDEPTNM', ''), 'target_dr': r.get('REFDOCNM', ''), 'status': status, 'reason': reason, 'report': r.get('REFRPT', '')})
            
            emg_notes = None
            opd_notes = None
            if vtype == 'EMG': emg_notes = self.get_emg_clinical_notes(caseno, user_id=user_id)
            elif vtype == 'OPD': opd_notes = self.get_opd_clinical_notes(caseno, user_id=user_id)
            
            return {'meds': meds, 'consults': consults, 'emg_notes': emg_notes, 'opd_notes': opd_notes}
        except Exception as e:
            print(f"[-] Error fetching visit details: {e}")
            return {'meds': [], 'consults': [], 'emg_notes': None, 'opd_notes': None}

    def get_opd_clinical_notes(self, caseno, user_id=None):
        """
        Fetches SOAP notes for OPD visits from OPDUSR.OPDSOAP.
        """
        try:
            q = f"SELECT SUBJCONTENT, OBJECONTENT, ASSECONTENT, PLANCONTENT FROM OPDUSR.OPDSOAP WHERE OPDCASENO = '{caseno}'"
            res = self._execute_sql_raw(q, user_id=user_id)
            if res and '<NewDataSet>' in res:
                rows = self._parse_sql_rows_raw(res)
                if rows:
                    r = rows[0]
                    return {'S': r.get('SUBJCONTENT', ''), 'O': r.get('OBJECONTENT', ''), 'A': r.get('ASSECONTENT', ''), 'P': r.get('PLANCONTENT', '')}
            return None
        except Exception as e:
            print(f"[-] Error fetching OPD notes: {e}")
            return None

    def get_emg_clinical_notes(self, caseno, user_id=None):
        """
        Fetches detailed EMG notes: Chief Complaint, PI, PH, PE, and POMR Progress Notes.
        """
        notes = {'triage': {}, 'adm_note': {}, 'progress_notes': []}
        try:
            # 1. Triage Data
            q_triage = f"SELECT * FROM COMMON.PAT_EMG_TRIAGE WHERE HCASENO = '{caseno}'"
            res_triage = self._execute_sql_raw(q_triage, user_id=user_id)
            if res_triage and '<NewDataSet>' in res_triage:
                rows = self._parse_sql_rows_raw(res_triage)
                if rows: notes['triage'] = rows[0]

            # 2. Admission Note
            q_adm = f"SELECT * FROM COMMON.PAT_EMG_NOTE_ADM WHERE ECASENO = '{caseno}'"
            res_adm = self._execute_sql_raw(q_adm, user_id=user_id)
            if res_adm and '<NewDataSet>' in res_adm:
                rows = self._parse_sql_rows_raw(res_adm)
                if rows: notes['adm_note'] = rows[0]

            # 3. Progress Notes (POMR)
            q_pomr = f"SELECT * FROM COMMON.PAT_EMG_NOTE_POMR WHERE ECASENO = '{caseno}' ORDER BY CREATEDT ASC"
            res_pomr = self._execute_sql_raw(q_pomr, user_id=user_id)
            if res_pomr and '<NewDataSet>' in res_pomr:
                p_notes = self._parse_sql_rows_raw(res_pomr)
                for pn in p_notes:
                    for k in ['S', 'O', 'A', 'P']:
                        if k not in pn: pn[k] = ''
                notes['progress_notes'] = p_notes
            return notes
        except Exception as e:
            print(f"[-] Error fetching EMG clinical notes: {e}")
            return notes

    def get_official_lab_reports(self, patient_id, user_id):
        """
        Fetches 'Status 68_Official Report' items from OpoQ0R1Form.aspx.
        """
        print(f"[*] Fetching official lab reports for Patient: {patient_id} (User: {user_id})...")
        url = f"http://10.10.246.73/ReportOrder/OpoQ0R1Form.aspx?sUSERID={user_id}&patientId={patient_id}&sOPDSection=&sOPDCaseNo="
        
        try:
            r = requests.get(url, timeout=10)
            content = r.text
            
            # Clean up whitespace for easier regex matching
            content = re.sub(r'\s+', ' ', content)
            
            # Find rows with Grid/GridAlt/GridSelected classes, capturing attributes and content
            rows = re.findall(r'<tr([^>]*class="(?:Grid|GridAlt|GridSelected)"[^>]*)>(.*?)</tr>', content)
            
            results = []
            for attrs, row_content in rows:
                cols = re.findall(r'<td.*?>(.*?)</td>', row_content)
                if len(cols) >= 8:
                    name = re.sub(r'<.*?>|&nbsp;', '', cols[1]).strip()
                    sample = re.sub(r'<.*?>|&nbsp;', '', cols[2]).strip()
                    status = re.sub(r'<.*?>|&nbsp;', '', cols[3]).strip()
                    order_ap_no = re.sub(r'<.*?>|&nbsp;', '', cols[7]).strip()
                    
                    # Extract detail URL from onclick event in attributes
                    url_match = re.search(r"load_page\('(.*?)'\)", attrs)
                    detail_url = url_match.group(1) if url_match else ""
                    
                    # Ensure absolute URL and decode HTML entities
                    if detail_url:
                        detail_url = html.unescape(detail_url)
                        if detail_url.startswith('/'):
                            detail_url = "http://10.10.246.73" + detail_url
                    
                    # Check if it is an official report (68) or working report (64)
                    if '64' in status or '68' in status or '正式' in status:
                        results.append({
                            "name": name,
                            "sample": sample,
                            "status": status,
                            "order_ap_no": order_ap_no,
                            "url": detail_url
                        })
            
            print(f"[*] Found {len(results)} official reports.")
            return results
            
        except Exception as e:
            print(f"[-] Error fetching official reports: {e}")
            return []

    def _parse_dataset(self, content):
        try:
            text = zlib.decompress(content).decode('utf-8', errors='replace')
            if "diffgr:diffgram" not in text: return {}
            match = re.search(r'<NewDataSet>(.*?)</NewDataSet>', text, re.DOTALL)
            if not match: return {}
            inner = match.group(1)
            row_tags = set(re.findall(r'<(\w+)\s+diffgr:id', inner))
            full_data = {}
            for tag in row_tags:
                rows = re.findall(f'<{tag}[^>]*>(.*?)</{tag}>', text, re.DOTALL)
                table_data = []
                for row in rows:
                    fields = re.findall(r'<(\w+)>(.*?)</\1>', row)
                    table_data.append({k: v for k, v in fields})
                full_data[tag] = table_data
            return full_data
        except: return {}
