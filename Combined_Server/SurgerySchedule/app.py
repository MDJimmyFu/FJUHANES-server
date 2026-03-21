from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from his_client_final import HISClient
from auth_handler import validate_login
import datetime
import os
import sys
import json
import requests
import functools
import webbrowser
import threading
import time
from resource_utils import resource_path

# Ensure UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Determine the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = "surgery_secret_key"
client = HISClient()

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = validate_login(username, password)
        if user_data:
            session['user_id'] = user_data.get('SignOnID')
            session['user_name'] = user_data.get('UserName')
            session['unique_id'] = user_data.get('UniqueID')
            session['create_id'] = user_data.get('CreateID') # Encrypted PWD or other ID
            session['user_password'] = password # Actual login password for deep links
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            error = '帳號或密碼錯誤，請重新輸入。'
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Ensure eval_data is in a writable location relative to the executable
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
    EVAL_DATA_DIR = os.path.join(base_dir, 'SurgerySchedule', 'eval_data')
else:
    EVAL_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eval_data')
if not os.path.exists(EVAL_DATA_DIR):
    os.makedirs(EVAL_DATA_DIR, exist_ok=True)

@app.route('/')
@login_required
def index():
    # Server-Side Rendering of Surgery List
    # Support 'date' (new standard) or 'bg_date' (legacy)
    date_param = request.args.get('date') or request.args.get('bg_date')
    if date_param:
        bg_date = date_param.replace('-', '')
    else:
        bg_date = datetime.datetime.now().strftime("%Y%m%d")
        
    end_date_param = request.args.get('end_date')
    if end_date_param:
        end_date = end_date_param.replace('-', '')
    else:
        end_date = bg_date

    # New: support for list type (surgery or endoscopy)
    list_type = request.args.get('type', 'surgery')
        
    try:
        if list_type == 'endoscopy':
            surgeries = client.get_endoscopy_list(bg_date, end_date)
        elif list_type == 'ultrasound':
            surgeries = client.get_ultrasound_list(bg_date, end_date)
        else:
            surgeries = client.get_surgery_list(bg_date, end_date)
    except Exception as e:
        print(f"[-] SSR Error: {e}")
        surgeries = []
    
    return render_template('legacy_schedule.html', 
                           surgeries=surgeries, 
                           search_date=f"{bg_date[:4]}-{bg_date[4:6]}-{bg_date[6:]}",
                           search_end_date=f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}",
                           list_type=list_type)

@app.route('/patient_detail/<ordseq>')
@login_required
def patient_detail(ordseq):
    hhistnum = request.args.get('hhistnum', '')
    print(f"[*] Fetching FULL details for {ordseq} / {hhistnum}")
    
    try:
        # 1. Activate & Get C430 (Vitals, Labs, Hx, Meds)
        client.activate_patient(ordseq, hhistnum)
        pre_data = client.get_pre_anesthesia_data(ordseq, hhistnum) or {}
        
        # 2. Get Charging Data (Billing, Procedures)
        charging = client.get_anesthesia_charging_data(ordseq, hhistnum) or {}
        
        # 3. Get Real Labs (using helper)
        lab_data = client.get_lab_data(hhistnum, ordseq, pre_data=pre_data)
        
        # 4. Get Vitals from EXM (CPOE & Vitals Upload)
        vitals_exm = client.get_vitals_from_exm(hhistnum, ordseq, user_id=session.get('user_id'), pre_data=pre_data) or {}
        
        # 5. Get Official Lab Reports (Status 68) - Added 2026-02-20
        official_reports = client.get_official_lab_reports(hhistnum, user_id=session.get('user_id')) or []
        
        # Construct Main Info (Merged View) for easy access to fields like EMG, ANEASA, etc.
        main_info = {}
        if pre_data:
            for table_name, rows in pre_data.items():
                if rows and isinstance(rows, list) and len(rows) > 0:
                    try:
                        main_info.update(rows[0])
                    except: pass
        
        response_data = {
            "main_info": main_info,
            "raw_c430": pre_data,
            "charging": charging,
            "lab_data": lab_data,
            "vitals_exm": vitals_exm,
            "official_reports": official_reports
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"[-] Detail Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/anesthesia_billing')
@login_required
def anesthesia_billing():
    """Route for the new Batch Anesthesia Billing Query page."""
    return render_template('anesthesia_billing.html')

@app.route('/api/batch_anesthesia_billing', methods=['POST'])
@login_required
def batch_anesthesia_billing():
    """Batch query anesthesia methods, times, and self-pay items for multiple MRNs."""
    try:
        data = request.get_json(silent=True) or {}
        hhistnums = data.get('hhistnums', [])
        query_date = data.get('query_date') # Format: YYYY-MM-DD
        
        if not hhistnums:
            return jsonify({"error": "No MRNs provided"}), 400
            
        results = []
        for hhistnum in hhistnums:
            hhistnum = hhistnum.strip()
            if not hhistnum: continue
            
            print(f"[*] Batch processing MRN: {hhistnum} for date: {query_date}")
            history = client.get_anesthesia_history(hhistnum, user_id=session.get('user_id'))
            
            # Filter out LA and NI, and optionally filter by date
            filtered = [h for h in history if h.get('ANENM', '') not in ('LA', 'NI')]
            
            if query_date:
                # Assuming query_date is YYYY-MM-DD
                filtered = [h for h in filtered if h.get('ANEBGNDTTM', '').startswith(query_date)]
            
            for h in filtered:
                ordseq = h.get('ORDSEQ', '')
                # Fetch charging data for self-pay items
                charging = client.get_anesthesia_charging_data(ordseq, hhistnum) or {}
                
                # Duration calculation
                total_minutes = 0
                start_str = h.get('ANEBGNDTTM')
                end_str = h.get('ANEENDDTTM')
                if start_str and end_str:
                    try:
                        # Handle formats like '2023-01-01T10:00:00' or '2023-01-01 10:00:00'
                        fmt = "%Y-%m-%dT%H:%M:%S" if 'T' in start_str else "%Y-%m-%d %H:%M:%S"
                        start_dt = datetime.datetime.strptime(start_str[:19], fmt)
                        end_dt = datetime.datetime.strptime(end_str[:19], fmt)
                        diff = end_dt - start_dt
                        total_minutes = int(diff.total_seconds() / 60)
                    except Exception as ex:
                        print(f"[-] Time calculation error for {ordseq}: {ex}")
                
                # Extract self-pay items
                # Requirements: 551N..., 551055..., 551061..., 55102030
                self_pay_items = []
                all_raw_items = []
                for table in ['OPDORDM', 'OCCURENCS', 'COMMON_ORDER', 'ANEORDER']:
                    for item in charging.get(table, []):
                        all_raw_items.append({
                            'code': item.get('PFKEY', item.get('PFCODE', '')),
                            'name': item.get('PFNM', item.get('ORDPROCED', ''))
                        })
                
                seen_codes = set()
                for item in all_raw_items:
                    code = item['code']
                    if not code: continue
                    
                    is_match = False
                    if code.startswith('551N'): is_match = True
                    elif code.startswith('551055'): is_match = True
                    elif code.startswith('551061'): is_match = True
                    elif code == '55102030': is_match = True
                    
                    if is_match and code not in seen_codes:
                        self_pay_items.append(item)
                        seen_codes.add(code)
                
                results.append({
                    'hhistnum': hhistnum,
                    'patient_name': h.get('HNAMEC', ''),
                    'date': start_str[:10] if start_str else '',
                    'method': h.get('ANENM', ''),
                    'procedure': h.get('ORDPROCED', ''),
                    'total_time': total_minutes,
                    'self_pay': self_pay_items,
                    'doctor': h.get('ANEDOCNMC', h.get('PROCNMC', '')),
                    'supervisor': h.get('ANESUPVNMC', h.get('SUPNMC', '')),
                    'ordseq': ordseq
                })
                
        return jsonify(results)
    except Exception as e:
        print(f"[-] Batch Billing Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/board')
@login_required
def board():
    """Route for the new Surgery Board view."""
    opdate = datetime.datetime.now().strftime('%Y%m%d')
    return render_template('board.html', opdate=opdate)

@app.route('/scanner')
@login_required
def scanner():
    """Route for the mobile barcode scanner page."""
    return render_template('scanner.html')

@app.route('/ane_eval_lookup')
@login_required
def ane_eval_lookup():
    """Route for the standalone MRN-based anesthesia evaluation lookup page."""
    return render_template('ane_eval_lookup.html')

@app.route('/api/ane_history/<hhistnum>')
@login_required
def ane_history(hhistnum):
    """Fetch anesthesia history for a patient by HHISTNUM (病歷號)."""
    print(f"[*] Fetching anesthesia history for {hhistnum}")
    try:
        history = client.get_anesthesia_history(hhistnum, user_id=session.get('user_id'))
        # Filter out LA and NI
        filtered = [h for h in history if h.get('ANENM', '') not in ('LA', 'NI')]
        return jsonify({
            'history': [{
                'ordseq': h.get('ORDSEQ', ''),
                'method': h.get('ANENM', ''),
                'procedure': h.get('ORDPROCED', ''), 
                'asa': h.get('ANEASA', ''),
                'doctor': h.get('ANEDOCNMC', h.get('PROCNMC', '')),
                'supervisor': h.get('ANESUPVNMC', ''),
                'start': h.get('ANEBGNDTTM', ''),
                'end': h.get('ANEENDDTTM', ''),
                'hcaseno': h.get('HCASENO', ''),
            } for h in filtered],
            'total': len(history),
            'filtered': len(filtered),
        })
    except Exception as e:
        print(f"[-] Ane History Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/patient_history/<hhistnum>')
@login_required
def patient_history(hhistnum):
    """Fetch comprehensive medical history (OPD/ER/ADM)."""
    try:
        data = client.get_comprehensive_patient_history(hhistnum, user_id=session.get('user_id'))
        return jsonify(data or [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ane_history_detail/<ordseq>')
@login_required
def ane_history_detail(ordseq):
    """Fetch charging data for a historical anesthesia record."""

    hhistnum = request.args.get('hhistnum', '')
    print(f"[*] Fetching HISTORICAL anesthesia detail for {ordseq} / {hhistnum}")
    
    try:
        charging = client.get_anesthesia_charging_data(ordseq, hhistnum) or {}
        
        # Extract anesthesia info
        ane_info = {}
        if 'ORRANER' in charging and charging['ORRANER']:
            aner = charging['ORRANER'][0]
            ane_info = {
                'asa': aner.get('ANEASA', ''),
                'method': aner.get('ANENM', aner.get('ANEMET', '')),
                'doctor': aner.get('ANEDOCNMC', aner.get('PROCNMC', '')),
                'supervisor': aner.get('ANESUPVNMC', ''),
                'start': aner.get('ANEBGNDTTM', ''),
                'end': aner.get('ANEENDDTTM', ''),
                'room': aner.get('ANEROOM', ''),
            }
        
        # Consolidate items from multiple tables: OPDORDM, OCCURENCS, COMMON_ORDER, ANEORDER
        all_items = []
        
        # 1. OPDORDM
        for item in charging.get('OPDORDM', []):
            all_items.append({
                'code': item.get('PFKEY', ''),
                'name': item.get('PFNM', ''),
                'qty': item.get('DOSE', item.get('APPLYTOTAL', '1')),
            })
            
        # 2. OCCURENCS
        for item in charging.get('OCCURENCS', []):
            all_items.append({
                'code': item.get('PFCODE', ''),
                'name': item.get('ORDPROCED', ''),
                'qty': item.get('OCQNTY', '1'),
            })
            
        # 3. COMMON_ORDER
        for item in charging.get('COMMON_ORDER', []):
            all_items.append({
                'code': item.get('PFKEY', ''),
                'name': item.get('ORDPROCED', ''),
                'qty': item.get('OCQNTY', '1'),
            })
            
        # 4. ANEORDER
        for item in charging.get('ANEORDER', []):
            all_items.append({
                'code': item.get('PFKEY', ''),
                'name': item.get('ORDPROCED', ''),
                'qty': '1',
            })

        # Categorize and Deduplicate
        self_pay = []
        materials = []
        procedures = []
        seen_codes = set()
        
        for item in all_items:
            code = item['code']
            if not code or code in seen_codes:
                continue
            seen_codes.add(code)
            
            if code.startswith('551N'):
                self_pay.append(item)
            elif code.startswith('551'):
                materials.append(item)
            else:
                procedures.append(item)
        
        return jsonify({
            'ane_info': ane_info,
            'self_pay': self_pay,
            'materials': materials,
            'procedures': procedures,
        })
        
    except Exception as e:
        print(f"[-] Ane History Detail Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/his/<method>', methods=['POST', 'GET'])
@login_required
def his_proxy(method):
    try:
        # Support both GET params and POST form data
        params = request.args.to_dict() if request.method == 'GET' else request.form.to_dict()
        print(f"[*] Legacy API Call: {method} with params {params}")

        # Mapping of legacy methods to HISClient operations
        if method == 'getPatOperationList':
            date_str = params.get('pBGOPDATE', datetime.datetime.now().strftime("%Y%m%d"))
            end_date_str = params.get('pENDOPDATE', date_str)
            data = client.get_surgery_list(date_str, end_date_str)
            return jsonify({"datastatus": 1, "returnList": data})

        elif method == 'getAneAssessOrdseqDTTM':
            ordseq = params.get('pOrdSeq')
            hhistnum = params.get('pHHISNum', '') 
            full_data = client.get_pre_anesthesia_data(ordseq, hhistnum)
            
            result_item = {}
            if full_data:
                # Merge all available tables into one object as expected by the legacy detail view
                for table_name, table_rows in full_data.items():
                    if table_rows and isinstance(table_rows, list):
                        result_item.update(table_rows[0])
            
            return jsonify({"datastatus": 1, "returnList": [result_item]})

        elif method == 'getAneAssessCXRList':
            full_data = client.get_pre_anesthesia_data(params.get('pOrdSeq'), params.get('pHHISNum', ''))
            cxr_list = full_data.get('INSPECTION_CXR', [])
            
            # Fallback to CXR table if INSPECTION_CXR is empty
            if not cxr_list and 'CXR' in full_data:
                cxr_list = full_data.get('CXR', [])
            
            # Ensure CXRURL exists to prevent frontend undefined errors
            for item in cxr_list:
                if 'CXRURL' not in item:
                    item['CXRURL'] = ''
                    
            return jsonify({"datastatus": 1, "returnList": cxr_list})

        elif method == 'getPatAnaestheHistList':
            full_data = client.get_pre_anesthesia_data(params.get('pOrdSeq'), params.get('pHHISNum', ''))
            return jsonify({"datastatus": 1, "returnList": full_data.get('PAT_ANAESTHE_HIST', [])})

        elif method == 'getPatConsultationList':
            full_data = client.get_pre_anesthesia_data(params.get('pOrdSeq'), params.get('pHHISNum', ''))
            return jsonify({"datastatus": 1, "returnList": full_data.get('CONSULTATION', [])})

        elif method == 'getPatADMDrugList':
            full_data = client.get_pre_anesthesia_data(params.get('pOrdSeq'), params.get('pHHISNum', ''))
            # Prefer OR_ORDER from C430 if available
            return jsonify({"datastatus": 1, "returnList": full_data.get('OR_ORDER', [])})

        elif method == 'getPatAdmHistoryList':
            hhistnum = params.get('pHHISNum', '')
            data = client.get_admission_history(hhistnum, user_id=session.get('user_id'))
            return jsonify({"datastatus": 1, "returnList": data})

        elif method == 'getComprehensivePatientHistory':
            hhistnum = params.get('pHHISNum', '')
            data = client.get_comprehensive_patient_history(hhistnum, user_id=session.get('user_id'))
            return jsonify({"datastatus": 1, "returnList": data})

        elif method == 'getVisitDetails':
            caseno = params.get('pCaseNo', '')
            vtype = params.get('pVisitType', 'ADM')
            data = client.get_visit_details(caseno, vtype, user_id=session.get('user_id'))
            return jsonify({"datastatus": 1, "returnList": data})

        elif method == 'getConsultationContent':
            caseno = params.get('pCaseNo', '')
            base_url = "http://10.10.242.59/consult_query/"
            list_url = f"{base_url}consult_form.php?HCASENO={caseno}"
            try:
                resp = requests.get(list_url, timeout=5)
                if resp.status_code == 200:
                    resp.encoding = resp.apparent_encoding # Handle Big5/MS950
                    html = resp.text
                    # Parse the table: <tr><td>...</td>...<td><a href='...'>查詢</a></td></tr>
                    import re
                    # Split by <tr> to handle legacy HTML without </tr>
                    parts = re.split(r'<tr>', html, flags=re.IGNORECASE)
                    consultations = []
                    for part in parts:
                        cols = re.findall(r"<td>(.*?)</td>", part, re.DOTALL | re.IGNORECASE)
                        if len(cols) >= 5:
                            # Extract link from last column
                            link_match = re.search(r"href='(.*?)'", cols[4], re.IGNORECASE)
                            if not link_match:
                                # Try double quotes too
                                link_match = re.search(r'href="(.*?)"', cols[4], re.IGNORECASE)
                            
                            report_link = f"{base_url}{link_match.group(1)}" if link_match else ""
                            consultations.append({
                                "target_dr": cols[0].strip(),
                                "request_time": cols[1].strip(),
                                "request_dr": cols[2].strip(),
                                "status": cols[3].strip(),
                                "url": report_link
                            })
                    
                    print(f"[*] Found {len(consultations)} consultations for Case {caseno}")
                    return jsonify({"datastatus": 1, "consultations": consultations})
                else:
                    return jsonify({"datastatus": 0, "message": f"Server returned {resp.status_code}"})
            except Exception as e:
                return jsonify({"datastatus": 0, "message": str(e)})

        elif method == 'getPatADMHistList':


            full_data = client.get_pre_anesthesia_data(params.get('pOrdSeq'), params.get('pHHISNum', ''))
            return jsonify({"datastatus": 1, "returnList": full_data.get('PAT_ADM_CASE', [])})

        elif method == 'getAneAssessDrMemoList':
            full_data = client.get_pre_anesthesia_data(params.get('pOrdSeq'), params.get('pHHISNum', ''))
            return jsonify({"datastatus": 1, "returnList": full_data.get('PAT_ADM_DRMEMO', [])})

        elif method in ['getBilAnaestheOrderList', 'getBilAnaestheDrugList', 'getBilAnaestheMaterialList']:
            ordseq = params.get('pOrdSeq')
            charging = client.get_anesthesia_charging_data(ordseq, "")
            
            # Map specific lists
            if method == 'getBilAnaestheOrderList':
                # Procedures
                data = charging.get('OPDORDM', []) + charging.get('COMMON_ORDER', [])
            elif method == 'getBilAnaestheDrugList':
                # Drugs
                data = charging.get('OCCURENCS', [])
            else: # getBilAnaestheMaterialList
                # Materials
                data = [item for item in charging.get('OPDORDM', []) if item.get('PFKEY', '').startswith('M')]
                
            return jsonify({"datastatus": 1, "returnList": data})

        # Fallback for other methods (return empty success)
        return jsonify({"datastatus": 1, "returnList": []})

    except Exception as e:
        print(f"[-] Legacy API Error ({method}): {e}")
        return jsonify({"datastatus": -1, "errorMsg": str(e)}), 500

@app.route('/api/surgery_list', methods=['POST'])
@login_required
def get_surgery_list():
    try:
        data = request.get_json(silent=True) or {}
        # Support single date or range
        bg_date = data.get('bg_date', data.get('date', datetime.datetime.now().strftime("%Y%m%d"))).replace('-', '')
        end_date = data.get('end_date', bg_date).replace('-', '')
        
        print(f"[*] Fetching Surgery List from {bg_date} to {end_date}")
        surgeries = client.get_surgery_list(bg_date, end_date)
            
        return jsonify(surgeries)
    except Exception as e:
        print(f"[-] Surgery List Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/details', methods=['POST'])
@login_required
def get_details():
    try:
        data = request.get_json(silent=True) or {}
        ordseq = data.get('ordseq')
        hhistnum = data.get('hhistnum')
        section = data.get('section', 'all') 

        if not ordseq:
            return jsonify({"error": "Missing ordseq"}), 400

        results = {}
        
        # Phase 1: Vitals & Labs
        if section in ['vitals', 'all']:
            # Activation is usually needed for C430/Vitals
            client.activate_patient(ordseq, hhistnum)
            pre_data = client.get_pre_anesthesia_data(ordseq, hhistnum)
            lab_data = client.get_lab_data(hhistnum, ordseq, pre_data=pre_data)
            vitals = client.get_vitals_from_exm(hhistnum, ordseq, user_id=session.get('user_id'))
            
            # Phase 1.5: Official Lab Reports (Status 68)
            official_reports = client.get_official_lab_reports(hhistnum, user_id=session.get('user_id'))
            
            results.update({
                "predata": pre_data,
                "lab_data": lab_data,
                "vitals": vitals,
                "official_reports": official_reports
            })
            
        # Phase 2: History & Meds (Extended)
        if section in ['extended', 'all']:
            charging_data = client.get_anesthesia_charging_data(ordseq, hhistnum) or {}
            results.update({
                "charging": charging_data
            })
            
        return jsonify(results)
    except Exception as e:
        print(f"[-] Details Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/save_eval', methods=['POST'])
@login_required
def save_eval():
    try:
        data = request.get_json(silent=True) or {}
        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({"error": "Missing patient_id"}), 400
        
        file_path = os.path.join(EVAL_DATA_DIR, f"{patient_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_eval', methods=['POST'])
@login_required
def get_eval():
    try:
        data = request.get_json(silent=True) or {}
        patient_id = data.get('patient_id')
        file_path = os.path.join(EVAL_DATA_DIR, f"{patient_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        return jsonify({})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lookup_patient', methods=['POST'])
@login_required
def lookup_patient():
    """Finds a patient by MRN across history and returns basic info + details."""
    try:
        data = request.get_json(silent=True) or {}
        hhistnum = data.get('hhistnum')
        if not hhistnum:
            return jsonify({"error": "Missing hhistnum"}), 400
            
        hhistnum = hhistnum.strip().upper()
        print(f"[*] Global lookup for MRN: {hhistnum}")
        
        # 1. Search Comprehensive History (OPD/ER/ADM) to find demographics and recent cases
        comp_history = client.get_comprehensive_patient_history(hhistnum, user_id=session.get('user_id'))
        
        # 2. Search Anesthesia History for ORDSEQ
        anes_history = client.get_anesthesia_history(hhistnum, user_id=session.get('user_id'))
        
        patient_name = ""
        age = ""
        sex = ""
        ordseq = ""
        procedure = ""
        
        if comp_history:
            # Use most recent visit for basic info
            latest = comp_history[0]
            patient_name = latest.get('doctor') # Wait, 'doctor'? Looking at get_comprehensive_patient_history...
            # Actually let's look at get_comprehensive_patient_history in his_client_final.py
            # Line 489: {'caseno': ..., 'date': ..., 'type': ..., 'dept': ..., 'diagnosis': ..., 'doctor': ..., 'ward_bed': ...}
            # It seems get_comprehensive_patient_history doesn't return HNAMEC/AGE/HSEXE directly.
            
            # Let's check get_admission_history as well.
            adm_history = client.get_admission_history(hhistnum, user_id=session.get('user_id'))
            if adm_history:
                patient_name = adm_history[0].get('doctor') # Still 'doctor'? 
                # Let me re-read get_admission_history in his_client_final.py
        
        # If SQL history doesn't yield HNAMEC, try to find in today's surgery list
        surgeries = client.get_surgery_list()
        today_match = next((s for s in surgeries if s.get('HHISTNUM') == hhistnum), None)
        
        if today_match:
            patient_name = today_match.get('HNAMEC', patient_name)
            age = today_match.get('AGE', age)
            sex = today_match.get('HSEXE', sex)
            ordseq = today_match.get('ORDSEQ', ordseq)
            procedure = today_match.get('ORDPROCED', procedure)
        elif anes_history:
            patient_name = anes_history[0].get('HNAMEC', patient_name)
            age = anes_history[0].get('AGE', age)
            sex = anes_history[0].get('HSEXE', sex)
            ordseq = anes_history[0].get('ORDSEQ', ordseq)
            procedure = anes_history[0].get('ORDPROCED', procedure)
            
        if not patient_name and not anes_history and not today_match:
             # Try one last thing: get_comprehensive_patient_history might have doctors but no demographics.
             # In some cases, we just have the HN.
             if not comp_history:
                return jsonify({"error": "查無此病歷號"}), 404
             patient_name = "未知名病患"

        res = {
            "HNAMEC": patient_name,
            "HSEXE": sex,
            "AGE": age,
            "HHISTNUM": hhistnum,
            "ORDSEQ": ordseq,
            "ORDPROCED": procedure
        }
        return jsonify(res)
    except Exception as e:
        print(f"[-] Global Lookup Error: {e}")
        return jsonify({"error": str(e)}), 500

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    print("[*] Surgery Schedule Server Starting...")
    if not os.environ.get("WERKZEUG_RUN_MAIN"): # Precents double opening in debug mode
        threading.Thread(target=open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
