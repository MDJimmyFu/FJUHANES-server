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
                # We need to pick specific Event Types
                # SPO2, BP.NBP, PULSE.USUAL, RESPIRATORY, BT.EAR
                
                # Dictionary to hold latest value for each type
                latest_vals = {}
                
                for row in rows:
                    # Parse row content
                    etype_m = re.search(r'<EVENT_TYPE>(.*?)</EVENT_TYPE>', row)
                    nval_m = re.search(r'<NVALUE1>(.*?)</NVALUE1>', row)
                    nval2_m = re.search(r'<NVALUE2>(.*?)</NVALUE2>', row)
                    date_m = re.search(r'<OCCURDATE>(.*?)</OCCURDATE>', row)
                    
                    if etype_m and nval_m:
                        etype = etype_m.group(1).strip()
                        val = nval_m.group(1).strip()
                        val2 = nval2_m.group(1).strip() if nval2_m else ""
                        dt = date_m.group(1).strip() if date_m else ""

                        # Only keep latest for each type
                        if etype not in latest_vals:
                            latest_vals[etype] = {'val': val, 'val2': val2, 'dt': dt}
            
            # Map Monitoring Vitals to Flat Structure
            if 'SPO2' in latest_vals:
                mapped['SPO2'] = latest_vals['SPO2']['val']
                mapped['SPO2_DTTM'] = latest_vals['SPO2']['dt']
            
            if 'BP.NBP' in latest_vals:
                sys = latest_vals['BP.NBP']['val']
                dia = latest_vals['BP.NBP']['val2']
                mapped['BP'] = f"{sys}/{dia}"
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

            return mapped
            
        except Exception as e:
            print(f"[-] Error in get_vitals_from_exm: {e}")
            return {}

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
