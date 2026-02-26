import requests
import zlib
import datetime
import re
import os
import sys
import time

class HISClient:
    def __init__(self, c250_template="c250_payload_1.bin", c430_template="c430_payload_0.bin", q050_template="q050_payload_0.bin"):
        self.base_url = "http://10.10.246.90:8800"
        self.c250_template = c250_template
        self.c430_template = c430_template
        self.q050_template = q050_template
        self.c250_activate_template = "c250_activate.bin"
        self.headers = {
            "Content-Type": "application/octet-stream",
            "X-Compress": "yes",
            "User-Agent": "Mozilla/4.0+(compatible; MSIE 6.0; Windows 6.2.9200.0; MS .NET Remoting; MS .NET CLR 2.0.50727.9164 )",
            "Expect": "100-continue",
            "Host": "10.10.246.90:8800",
            "Connection": "Keep-Alive"
        }

    def get_surgery_list(self, date_str=None):
        """
        Fetches the surgery list for the given date (YYYYMMDD).
        """
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            
        print(f"[*] Fetching surgery list for {date_str}...")
        
        try:
            with open(self.c250_template, "rb") as f:
                compressed_template = f.read()
            decompressed = zlib.decompress(compressed_template)
            
            target_date_bytes = date_str.encode('ascii')
            # Template has 20260211
            patched_payload = decompressed.replace(b"20260211", target_date_bytes)
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

            # Template values from Request 1318
            template_hhistnum = b"003617083J"
            template_ordseq = b"A75176986OR0041"

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
            
            if template_hhistnum not in decompressed:
                 print("[-] Error: Template HHISTNUM not found in payload.")
                 return None
            
            patched_payload = decompressed.replace(template_hhistnum, hhistnum.encode('ascii'))
            patched_payload = patched_payload.replace(template_ordseq, ordseq.encode('ascii'))
            
            if opdate:
                # Patch all occurrences of the template date
                patched_payload = patched_payload.replace(template_opdate, opdate.encode('ascii'))
            else:
                # Default to today if not provided? Or just leave template?
                # Better to use today's date if we're doing live queries
                today = datetime.datetime.now().strftime("%Y%m%d")
                patched_payload = patched_payload.replace(template_opdate, today.encode('ascii'))

            final_payload = zlib.compress(patched_payload)
            
            response = requests.post(f"{self.base_url}/HISOrmC430Facade", data=final_payload, headers=self.headers)
            response.raise_for_status()
            
            return self._parse_dataset(response.content)
            
        except Exception as e:
            print(f"[-] Error fetching pre-anesthesia data: {e}")
            return None

    def get_anesthesia_charging_data(self, ordseq, hhistnum):
        """
        Fetches anesthesia charging data (Q050) for the given ORDSEQ and HHISTNUM.
        """
        print(f"[*] Fetching anesthesia charging data for {ordseq} / {hhistnum}...")
        
        try:
            with open(self.q050_template, "rb") as f:
                compressed_template = f.read()
            decompressed = zlib.decompress(compressed_template)
            
            # Template values from pcap
            template_hhistnum = b"003162935D"
            template_ordseq = b"A75072943OR0001"
            
            if template_hhistnum not in decompressed:
                 print("[-] Error: Template HHISTNUM not found in Q050 payload.")
                 return None
            
            patched_payload = decompressed.replace(template_hhistnum, hhistnum.encode('ascii'))
            patched_payload = patched_payload.replace(template_ordseq, ordseq.encode('ascii'))
            final_payload = zlib.compress(patched_payload)
            
            response = requests.post(f"{self.base_url}/HISOrmQ050Facade", data=final_payload, headers=self.headers)
            response.raise_for_status()
            
            return self._parse_dataset(response.content)
            
        except Exception as e:
            print(f"[-] Error fetching anesthesia charging data: {e}")
            return None

    def _parse_surgery_list(self, content):
        try:
            text = zlib.decompress(content).decode('utf-8', errors='replace')
            entries = []
            rows = re.findall(r'<ORDOP_OPSTA[^>]*>(.*?)</ORDOP_OPSTA>', text, re.DOTALL)
            for row in rows:
                item = {}
                # Extract all tags specifically to avoid missing fields
                # Use findall to get (tag, value) tuples
                tags = re.findall(r'<(\w+)>(.*?)</\1>', row)
                for tag, value in tags:
                    item[tag] = value.strip()
                if item:
                    entries.append(item)
            return entries
        except Exception as e:
            print(f"[-] Parse error: {e}")
            return []

    def get_vitals_from_exm(self, hhistnum, ordseq=None):
        """
        Fetches vitals from CPOE.OR_SIGN_IN (Weight/Height) and OPDUSR.VITALSIGNUPLOAD (Monitoring).
        """
        print(f"[*] Fetching accurate vitals from EXM for {hhistnum} / {ordseq}...")
        try:
            # Helper to execute SQL via EXM template
            def execute_sql_inner(sql_query):
                template_path = "HISExmFacade_payload_0.bin"
                if not os.path.exists(template_path): return None
                with open(template_path, "rb") as f:
                    compressed_template = f.read()
                try: decompressed = zlib.decompress(compressed_template)
                except: decompressed = compressed_template
                original_sql_bytes = b"SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'"
                target_len = len(original_sql_bytes)
                if len(sql_query) > target_len:
                    print(f"[-] SQL too long: {len(sql_query)} > {target_len}")
                    return None
                padded_sql = sql_query.ljust(target_len)
                patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
                final_payload = zlib.compress(patched_payload)
                resp = requests.post(f"{self.base_url}/HISExmFacade", data=final_payload, headers=self.headers)
                if resp.status_code == 200:
                    dec = zlib.decompress(resp.content)
                    return dec.decode('utf-8', errors='ignore')
                return None

            mapped = {}
            import re

            # 1. Fetch Weight/Height from CPOE.OR_SIGN_IN using ORDSEQ (Most accurate for surgery)
            if ordseq:
                q_or = f"SELECT * FROM CPOE.OR_SIGN_IN WHERE ORDSEQ = '{ordseq}'"
            else:
                q_or = f"SELECT * FROM CPOE.OR_SIGN_IN WHERE HHISNUM = '{hhistnum}'"
            
            res_or = execute_sql_inner(q_or)
            if res_or and "<NewDataSet>" in res_or:
                # Find latest seq
                rows = re.findall(r'<DRMODIFY.*?>(.*?)</DRMODIFY>', res_or, re.DOTALL)
                # Sort by SEQ desc?
                # Simple extraction of first match with W/H
                for row in rows:
                    w = re.search(r'<WEIGHT>(.*?)</WEIGHT>', row)
                    h = re.search(r'<HEIGHT>(.*?)</HEIGHT>', row)
                    # Timestamp?
                    
                    if w and w.group(1): 
                        mapped['WEIGHT'] = w.group(1)
                        # Optional: Add DTTM if available in CPOE
                    if h and h.group(1):
                        mapped['HEIGHT'] = h.group(1)
                    # If found both, break?
                    if 'WEIGHT' in mapped and 'HEIGHT' in mapped: break

            # 2. Fetch Monitoring Vitals from OPDUSR.VITALSIGNUPLOAD (Latest)
            q_upload = f"SELECT * FROM OPDUSR.VITALSIGNUPLOAD WHERE HHISNUM = '{hhistnum}' ORDER BY OCCURDATE DESC"
            res_up = execute_sql_inner(q_upload)
            
            if res_up and "<NewDataSet>" in res_up:
                rows = re.findall(r'<DRMODIFY.*?>(.*?)</DRMODIFY>', res_up, re.DOTALL)
                # Dictionary to hold latest value for each type
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
                
                if 'BP.NBP' in latest_vals:
                    sys_v = latest_vals['BP.NBP']['val']
                    dia_v = latest_vals['BP.NBP']['val2']
                    mapped['BP'] = f"{sys_v}/{dia_v}"
                    mapped['BP_DTTM'] = latest_vals['BP.NBP']['dt']
                
                if 'PULSE.USUAL' in latest_vals:
                    mapped['PULSE'] = latest_vals['PULSE.USUAL']['val']
                    mapped['PULSE_DTTM'] = latest_vals['PULSE.USUAL']['dt']
                
                if 'RESPIRATORY' in latest_vals:
                    mapped['RESP'] = latest_vals['RESPIRATORY']['val']
                    mapped['RESP_DTTM'] = latest_vals['RESPIRATORY']['dt']
                
                if 'BT.EAR' in latest_vals:
                    mapped['BT'] = latest_vals['BT.EAR']['val']
                    mapped['BT_DTTM'] = latest_vals['BT.EAR']['dt']

                # Fallback for HEIGHT/WEIGHT if not found or 0 in OR_SIGN_IN
                if mapped.get('HEIGHT', '0') == '0' and 'HEIGHT' in latest_vals:
                    mapped['HEIGHT'] = latest_vals['HEIGHT']['val']
                    mapped['HEIGHT_DTTM'] = latest_vals['HEIGHT']['dt']
                if mapped.get('WEIGHT', '0') == '0' and 'WEIGHT' in latest_vals:
                    mapped['WEIGHT'] = latest_vals['WEIGHT']['val']
                    mapped['WEIGHT_DTTM'] = latest_vals['WEIGHT']['dt']
                
                # Check for alternative naming "BODY HEIGHT" / "BODY WEIGHT"
                if mapped.get('HEIGHT', '0') == '0' and 'BODY HEIGHT' in latest_vals:
                    mapped['HEIGHT'] = latest_vals['BODY HEIGHT']['val']
                if mapped.get('WEIGHT', '0') == '0' and 'BODY WEIGHT' in latest_vals:
                    mapped['WEIGHT'] = latest_vals['BODY WEIGHT']['val']

            return mapped
            
        except Exception as e:
            print(f"[-] Error in get_vitals_from_exm: {e}")
            return {}

    def get_anesthesia_history(self, hhistnum):
        """
        Fetches anesthesia history for a patient using HHISTNUM (病歷號).
        Uses EXM SQL: HHISNUM -> SYSTEM.PAT_ADM_CASE (HCASENO) -> OPDUSR.ORRANER (ORDSEQ, method, ASA, etc.)
        Returns a list of dicts with ORDSEQ, ANENM, ANEASA, ANEBGNDTTM, ANEENDDTTM, HCASENO, etc.
        """
        print(f"[*] Fetching anesthesia history via SQL for {hhistnum}...")
        try:
            # Reuse EXM SQL helper
            def execute_sql_inner(sql_query):
                template_path = "HISExmFacade_payload_0.bin"
                if not os.path.exists(template_path): return None
                with open(template_path, "rb") as f:
                    compressed_template = f.read()
                try: decompressed = zlib.decompress(compressed_template)
                except: decompressed = compressed_template
                original_sql_bytes = b"SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'"
                target_len = len(original_sql_bytes)
                if len(sql_query) > target_len:
                    print(f"[-] SQL too long: {len(sql_query)} > {target_len}")
                    return None
                padded_sql = sql_query.ljust(target_len)
                patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
                final_payload = zlib.compress(patched_payload)
                resp = requests.post(f"{self.base_url}/HISExmFacade", data=final_payload, headers=self.headers)
                if resp.status_code == 200:
                    dec = zlib.decompress(resp.content)
                    return dec.decode('utf-8', errors='ignore')
                return None

            def parse_sql_rows(text):
                rows = re.findall(r'<DRMODIFY[^>]*>(.*?)</DRMODIFY>', text, re.DOTALL)
                results = []
                for row in rows:
                    fields = re.findall(r'<(\w+)>(.*?)</\1>', row)
                    results.append({k: v for k, v in fields})
                return results

            # Step 1: Get HCASENO from SYSTEM.PAT_ADM_CASE
            q1 = f"SELECT HCASENO FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhistnum}'"
            res1 = execute_sql_inner(q1)
            if not res1 or '<NewDataSet>' not in res1:
                print(f"  [-] No case numbers found for {hhistnum}")
                return []
            
            case_rows = parse_sql_rows(res1)
            casenums = list(set([r.get('HCASENO', '') for r in case_rows if r.get('HCASENO')]))
            print(f"  [+] Found {len(casenums)} case number(s)")

            # Step 2: For each HCASENO, query OPDUSR.ORRANER
            all_history = []
            for cn in casenums:
                q2 = f"SELECT * FROM OPDUSR.ORRANER WHERE HCASENO = '{cn}' AND CANCELYN = 'N'"
                res2 = execute_sql_inner(q2)
                if res2 and '<NewDataSet>' in res2:
                    rows = parse_sql_rows(res2)
                    for r in rows:
                        r['HCASENO'] = cn
                    all_history.extend(rows)
            
            # Step 3: Fetch Procedure Name & Billing Status from OPDUSR.OPDORDM
            # (User Requirement: Only show Billed items + Show Procedure Name)
            if all_history:
                # Get Procedure details for these cases
                # Query per case to avoid SQL length limit (115 bytes)
                opd_map = {} # ORDSEQ -> {PFNM, CHARGEFLAG}
                
                for cn in casenums:
                    # Note: We query by OPDCASENO (which matches HCASENO from PAT_ADM_CASE)
                    q3 = f"SELECT * FROM OPDUSR.OPDORDM WHERE OPDCASENO = '{cn}' AND CANCELYN = 'N'"
                    res3 = execute_sql_inner(q3)
                    
                    if res3 and '<NewDataSet>' in res3:
                        opd_rows = parse_sql_rows(res3)
                        for r in opd_rows:
                            # Map by ORDSEQ (assuming 1:1 for main procedure or we take the first)
                            oseq = r.get('ORDSEQ')
                            if oseq:
                                # Prefer items with ORDTYPE='OR' if duplicates exist, but simple map is OK for now
                                # If we see multiple, the last one overwrites. 
                                # We want the main procedure. Usually there is one main procedure per surgery.
                                opd_map[oseq] = {
                                    'PFNM': r.get('PFNM', ''),
                                    'CHARGEFLAG': r.get('CHARGEFLAG', 'N')
                                }
                
                # Filter and Enrich
                final_history = []
                for h in all_history:
                    oseq = h.get('ORDSEQ')
                    if oseq in opd_map:
                        details = opd_map[oseq]
                        # Filter: Must be Billed (CHARGEFLAG == 'Y')
                        if details['CHARGEFLAG'] == 'Y':
                            h['ORDPROCED'] = details['PFNM']
                            final_history.append(h)
                    else:
                        # If no matching OPDORDM record, strictly skip? 
                        # Or keep if user just wants "history"? 
                        # User said "只要顯示已計價" -> Only show billed. 
                        # If missing OPDORDM, we assume unbilled/unknown.
                        pass
                
                all_history = final_history

            # Sort by ANEBGNDTTM descending (most recent first)
            # Sort by ANEBGNDTTM descending (most recent first)
            all_history.sort(key=lambda x: x.get('ANEBGNDTTM', ''), reverse=True)
            
            # 2026-02-20: Filter out unbilled records (Missing COST_ID)
            # User reported 003457263J has unbilled records that should be hidden.
            # Only the billed record has "COST_ID": "ANES".
            all_history = [h for h in all_history if h.get('COST_ID')]
            
            print(f"  [+] Total billed anesthesia history records: {len(all_history)}")
            return all_history

        except Exception as e:
            print(f"[-] Error in get_anesthesia_history: {e}")
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
        except Exception as e:
            print(f"[-] Parse error: {e}")
            return {}

    def _execute_sql_raw(self, sql_query):
        """
        Executes a raw SQL query using the HISExmFacade.
        """
        template_path = "HISExmFacade_payload_0.bin"
        if not os.path.exists(template_path): return None
        with open(template_path, "rb") as f:
            compressed_template = f.read()
        try: decompressed = zlib.decompress(compressed_template)
        except: decompressed = compressed_template
        original_sql_bytes = b"SELECT * FROM BASCODE WHERE SYSTEMID = 'ORMPRJ' AND SYSCODETYPE = 'OF' AND HISSYSCODE = 'A03772' AND CANCELYN = 'N'"
        target_len = len(original_sql_bytes)
        if len(sql_query) > target_len:
            print(f"[-] SQL too long: {len(sql_query)} > {target_len}")
            return None
        padded_sql = sql_query.ljust(target_len)
        patched_payload = decompressed.replace(original_sql_bytes, padded_sql.encode('utf-8'))
        final_payload = zlib.compress(patched_payload)
        try:
            resp = requests.post(f"{self.base_url}/HISExmFacade", data=final_payload, headers=self.headers)
            if resp.status_code == 200:
                dec = zlib.decompress(resp.content)
                return dec.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"[-] Error executing SQL: {e}")
        return None

    def _parse_sql_rows_raw(self, text, tag="DRMODIFY"):
        if not text: return []
        rows = re.findall(f'<{tag}[^>]*>(.*?)</{tag}>', text, re.DOTALL)
        results = []
        for row in rows:
            # Add re.DOTALL to capture multiline content like clinical notes
            fields = re.findall(r'<(\w+)>(.*?)</\1>', row, re.DOTALL)
            results.append({k: v for k, v in fields})
        return results

    def get_admission_history(self, hhistnum):
        """
        Fetches hospitalization history from PAT_ADM_CASE for a given HHISNUM.
        """
        try:
            # Query PAT_ADM_CASE
            q = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhistnum}' ORDER BY HADMDT DESC"
            res = self._execute_sql_raw(q)
            
            history = []
            if res and '<NewDataSet>' in res:
                rows = self._parse_sql_rows_raw(res)
                for r in rows:
                    history.append({
                        'hcaseno': r.get('HCASENO', ''),
                        'admdt': r.get('HADMDT', ''),
                        'admtm': r.get('HADMTM', ''),
                        'disdt': r.get('HDISDT', ''),
                        'distm': r.get('HDISTM', ''),
                        'dept': r.get('HINCURSVCL', ''),
                        'ward': r.get('HNURSTA', ''),
                        'bed': r.get('HBED', ''),
                        'diagnosis': r.get('HINDIAG', ''),
                        'diagnosis_desc': r.get('HINDIAGDESC', ''),
                        'doctor': r.get('HVDOCNM', ''),
                        'patstat': r.get('HPATSTAT', '')
                    })
            return history
        except Exception as e:
            print(f"[-] Error fetching admission history: {e}")
            return []

    def get_comprehensive_patient_history(self, hhistnum):
        """
        Fetches a combined list of Outpatient, Emergency, and Inpatient visits.
        """
        try:
            # 1. Fetch ADM/EMG from systemic PAT_ADM_CASE
            adm_query = f"SELECT * FROM SYSTEM.PAT_ADM_CASE WHERE HHISNUM = '{hhistnum}' ORDER BY HADMDT DESC"
            adm_res = self._execute_sql_raw(adm_query)
            adm_list = []
            if adm_res and '<NewDataSet>' in adm_res:
                rows = self._parse_sql_rows_raw(adm_res)
                for r in rows:
                    vtype = 'EMG' if r.get('HINCURSVCL') == 'EMG' else 'ADM'
                    adm_list.append({
                        'caseno': r.get('HCASENO', ''),
                        'date': r.get('HADMDT', ''),
                        'type': vtype,
                        'dept': r.get('HINCURSVCL', ''),
                        'diagnosis': r.get('HINDIAG', ''),
                        'diagnosis_desc': r.get('HINDIAGDESC', ''),
                        'doctor': r.get('HVDOCNM', ''),
                        'ward_bed': f"{r.get('HNURSTA','')}-{r.get('HBED','')}" if vtype == 'ADM' else r.get('HNURSTA',''),
                        'dis_date': r.get('HDISDT', '')
                    })

            # 2. Fetch OPD from OPDUSR.OPDDIAG (Outpatient)
            # Grouping by OPDCASENO to get visit events
            opd_query = f"SELECT * FROM OPDUSR.OPDDIAG WHERE HHISNUM = '{hhistnum}' ORDER BY CREATEDATETIME DESC"
            opd_res = self._execute_sql_raw(opd_query)
            opd_visits = {} # OPDCASENO -> Visit Record
            if opd_res and '<NewDataSet>' in opd_res:
                rows = self._parse_sql_rows_raw(opd_res)
                for r in rows:
                    cn = r.get('OPDCASENO')
                    if not cn: continue
                    if cn not in opd_visits:
                        opd_visits[cn] = {
                            'caseno': cn,
                            'date': r.get('CREATEDATETIME', '')[:8] if r.get('CREATEDATETIME') else '',
                            'type': 'OPD',
                            'dept': '', # Will fill from other source or leave if not found
                            'diagnosis': r.get('DXNMC', ''),
                            'diagnosis_desc': r.get('DXNME', ''),
                            'doctor': r.get('PROCNMC', ''),
                            'ward_bed': '',
                            'dis_date': ''
                        }
            
            # Combine
            # Deduplicate: If an OPDCASENO is already in adm_list (as ADM or EMG), skip it in opd_visits
            adm_casenos = {a['caseno'] for a in adm_list if a.get('caseno')}
            
            combined_opd = []
            for cn, visit in opd_visits.items():
                if cn not in adm_casenos:
                    combined_opd.append(visit)
            
            all_history = adm_list + combined_opd
            # Sort by date descending
            all_history.sort(key=lambda x: x['date'], reverse=True)
            
            return all_history
        except Exception as e:
            print(f"[-] Error in comprehensive history: {e}")
            return []

    def get_visit_details(self, caseno, vtype='ADM'):
        """
        Fetches medications and consultations for a specific visit.
        """
        try:
            # 1. Fetch Medications from OPDORDM
            # Strategy: Query all ORTYPE='OD' (Medications) for this case
            med_query = f"SELECT * FROM OPDUSR.OPDORDM WHERE OPDCASENO = '{caseno}' AND ORTYPE = 'OD' AND CANCELYN = 'N'"
            med_res = self._execute_sql_raw(med_query)
            meds = []
            if med_res and '<NewDataSet>' in med_res:
                rows = self._parse_sql_rows_raw(med_res)
                for r in rows:
                    meds.append({
                        'name': r.get('PFNM', ''),
                        'dose': f"{r.get('DOSE','')} {r.get('GIVUNIT','')}",
                        'freq': r.get('FREQUENCY', ''),
                        'route': r.get('ROUTE', ''),
                        'memo': r.get('ORDERMEMO', '')
                    })

            # 2. Fetch Consultations from OPDREFM (Referrals)
            cons_query = f"SELECT * FROM OPDUSR.OPDREFM WHERE OPDCASENO = '{caseno}' AND CANCELYN = 'N'"
            cons_res = self._execute_sql_raw(cons_query)
            consults = []
            if cons_res and '<NewDataSet>' in cons_res:
                rows = self._parse_sql_rows_raw(cons_res)
                for r in rows:
                    # Filter: Status 'I' usually means incomplete/draft or ghost.
                    # Also ignore if reason is just a code like '50' with Status 'I'
                    status = r.get('REFINSTATUS', '')
                    reason = r.get('REFINREASON', '')
                    if status == 'I' and reason == '50':
                        continue
                        
                    consults.append({
                        'dept': r.get('OPDSECTION', ''),
                        'doctor': r.get('OPDDRNMC', ''),
                        'reason': reason,
                        'status': status,
                        'date': r.get('OPDREFINDATE', '')
                    })
            
            emg_notes = None
            opd_notes = None
            if vtype == 'EMG':
                emg_notes = self.get_emg_clinical_notes(caseno)
            elif vtype == 'OPD':
                opd_notes = self.get_opd_clinical_notes(caseno)
            
            return {'meds': meds, 'consults': consults, 'emg_notes': emg_notes, 'opd_notes': opd_notes}
        except Exception as e:
            print(f"[-] Error fetching visit details: {e}")
            return {'meds': [], 'consults': [], 'emg_notes': None, 'opd_notes': None}

    def get_opd_clinical_notes(self, caseno):
        """
        Fetches SOAP notes for OPD visits from OPDUSR.OPDSOAP.
        """
        try:
            q = f"SELECT SUBJCONTENT, OBJECONTENT, ASSECONTENT, PLANCONTENT FROM OPDUSR.OPDSOAP WHERE OPDCASENO = '{caseno}'"
            res = self._execute_sql_raw(q)
            if res and '<NewDataSet>' in res:
                rows = self._parse_sql_rows_raw(res)
                if rows:
                    r = rows[0]
                    return {
                        'S': r.get('SUBJCONTENT', ''),
                        'O': r.get('OBJECONTENT', ''),
                        'A': r.get('ASSECONTENT', ''),
                        'P': r.get('PLANCONTENT', '')
                    }
            return None
        except Exception as e:
            print(f"[-] Error fetching OPD notes: {e}")
            return None

    def get_emg_clinical_notes(self, caseno):
        """
        Fetches detailed EMG notes: Chief Complaint, PI, PH, PE, and POMR Progress Notes.
        """
        notes = {
            'triage': {},
            'adm_note': {},
            'progress_notes': []
        }
        try:
            # 1. Triage Data (Chief Complaint, Vitals)
            q_triage = f"SELECT * FROM COMMON.PAT_EMG_TRIAGE WHERE HCASENO = '{caseno}'"
            res_triage = self._execute_sql_raw(q_triage)
            if res_triage and '<NewDataSet>' in res_triage:
                rows = self._parse_sql_rows_raw(res_triage)
                if rows:
                    notes['triage'] = rows[0]

            # 2. Admission Note (Medical History, Physical Exam)
            q_adm = f"SELECT * FROM COMMON.PAT_EMG_NOTE_ADM WHERE ECASENO = '{caseno}'"
            res_adm = self._execute_sql_raw(q_adm)
            if res_adm and '<NewDataSet>' in res_adm:
                rows = self._parse_sql_rows_raw(res_adm)
                if rows:
                    notes['adm_note'] = rows[0]

            # 3. Progress Notes (POMR)
            q_pomr = f"SELECT * FROM COMMON.PAT_EMG_NOTE_POMR WHERE ECASENO = '{caseno}' ORDER BY CREATEDT ASC"
            res_pomr = self._execute_sql_raw(q_pomr)
            if res_pomr and '<NewDataSet>' in res_pomr:
                p_notes = self._parse_sql_rows_raw(res_pomr)
                # Ensure SOAP keys exist to avoid undefined in JS
                for pn in p_notes:
                    for k in ['S', 'O', 'A', 'P']:
                        if k not in pn: pn[k] = ''
                notes['progress_notes'] = p_notes

            return notes
        except Exception as e:
            print(f"[-] Error fetching EMG clinical notes: {e}")
            return notes

    def _extract_tag(self, snippet, tag):
        match = re.search(f"<{tag}>(.*?)</{tag}>", snippet)
        return match.group(1) if match else ""

    def get_lab_data(self, hhistnum, ordseq=None, pre_data=None):
        """
        Fetches lab data for the given hhistnum.
        If ordseq is provided, it tries to extract it from the pre-anesthesia data (C430).
        """
        print(f"[*] Fetching lab data for {hhistnum} (ORDSEQ: {ordseq})...")
        
        # Mapping from HIS titles to frontend keys
        mapping = {
            'WBC': 'WBC',
            'HGB': 'HB',
            'HCT': 'HCT',
            'PLT': 'PLT',
            'GLU RANDOM': 'Glucose',
            'PT': 'PT',
            'APTT': 'PTT',
            'INR': 'INR',
            'NA': 'Na',
            'K': 'K',
            'ALT': 'ALT',
            'AST': 'AST',
            'CREA': 'Cre',
            'BUN': 'BUN',
            'BIL': 'T_BIL',
            'CL': 'Cl',
            'CA': 'Ca'
        }

        lab_results = {}
        found_in_live = False
        
        # 1. Try to get from C430 if ORDSEQ available
        if ordseq and not pre_data:
            pre_data = self.get_pre_anesthesia_data(ordseq, hhistnum)
            
        if pre_data and 'INSPECTION' in pre_data:
                found_in_live = True
                print(f"[+] Found {len(pre_data['INSPECTION'])} labs in live data.")
                for item in pre_data['INSPECTION']:
                    title = item.get('TITLE', '').upper()
                    val = item.get('SYB_VALUE', '')
                    if title in mapping:
                        lab_results[mapping[title]] = val
                    elif 'GLUCOSE' in title:
                        lab_results['Glucose'] = val

        return lab_results

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    client = HISClient()
    
    # 1. Get List
    surgeries = client.get_surgery_list()
    if surgeries:
        print(f"\n[+] Found {len(surgeries)} surgeries today.")
        print(f"{'#':<3} | {'Patient':<10} | {'Procedure':<30} | {'Doctor'}")
        print("-" * 70)
        for i, s in enumerate(surgeries[:10]):
            print(f"{i:<3} | {s['patient']:<10} | {s['procedure'][:30]:<30} | {s['doctor']}")
        
        # 2. Get Detail for first patient
        target = surgeries[0]
        print(f"\n[*] Fetching details for {target['patient']}...")
        details = client.get_pre_anesthesia_data(target['ordseq'], target['hhistnum'])
        
        if details:
            print(f"[+] Retrieved {len(details)} tables of PRE-ANESTHESIA data.")
            
        # 3. Get Charging Data
        print(f"\n[*] Fetching CHARGING details for {target['patient']}...")
        charging = client.get_anesthesia_charging_data(target['ordseq'], target['hhistnum'])
        if charging:
             print(f"[+] Retrieved {len(charging)} tables of CHARGING data.")
             
             # 1. Anesthesia Info
             if 'ORRANER' in charging and charging['ORRANER']:
                 aner = charging['ORRANER'][0]
                 print(f"\n--- Anesthesia Info ---")
                 # Calculate Duration
                 start = aner.get('ANEBGNDTTM')
                 end = aner.get('ANEENDDTTM')
                 if start and end:
                     try:
                        # Simple string parse, assuming fixed format from output
                        # 2026-02-12T09:14:00+08:00
                        # We can just print the raw strings for now or simple diff
                        print(f"  Duration: {start} -> {end}")
                     except:
                        pass
                 
                 print(f"  Anesthesiologist: {aner.get('ANEDOCNMC', aner.get('PROCNMC', 'N/A'))}")
                 print(f"  Supervisor: {aner.get('ANESUPVNMC', 'N/A')}")
                 print(f"  ASA Class: {aner.get('ANEASA', 'N/A')}")

             # 2. Charging/Procedures
             if 'OPDORDM' in charging and charging['OPDORDM']:
                 materials = []
                 procedures = []
                 
                 for item in charging['OPDORDM']:
                     code = item.get('PFKEY', '')
                     if code.startswith('M'):
                         materials.append(item)
                     else:
                         procedures.append(item)
                 
                 if procedures:
                     print(f"\n--- Procedures & Billing (OPDORDM) ---")
                     print(f"{'Code':<12} | {'Name':<40} | {'Qty'}")
                     print("-" * 65)
                     for item in procedures:
                         print(f"{item.get('PFKEY',''):<12} | {item.get('PFNM',''):<40} | {item.get('DOSE','')}")

             if 'COMMON_ORDER' in charging and charging['COMMON_ORDER']:
                 print(f"\n--- Anesthesia Items (COMMON_ORDER) ---")
                 print(f"{'Code':<12} | {'Name':<40}")
                 print("-" * 65)
                 for item in charging['COMMON_ORDER']:
                     code = item.get('PFCODE', '')
                     name = item.get('ORDPROCED', '')
                     print(f"{code:<12} | {name:<40}")

             if 'OCCURENCS' in charging and charging['OCCURENCS']:
                 print(f"\n--- Occurrences (OCCURENCS) ---")
                 print(f"{'Code':<12} | {'Name':<40} | {'Qty'}")
                 print("-" * 65)
                 for item in charging['OCCURENCS']:
                     code = item.get('PFCODE', '')
                     name = item.get('ORDPROCED', '')
                     qty = item.get('OCQNTY', '')
                     print(f"{code:<12} | {name:<40} | {qty}")

             if 'OPDORDM' in charging and charging['OPDORDM']:
                 if materials:
                     print(f"\n--- Materials (材料費) ---")
                     print(f"{'Code':<12} | {'Name':<40} | {'Qty'}")
                     print("-" * 65)
                     for item in materials:
                         print(f"{item.get('PFKEY',''):<12} | {item.get('PFNM',''):<40} | {item.get('DOSE','')}")
        else:
             print("[-] No charging data found.")

    else:
        print("[-] No surgeries found.")
