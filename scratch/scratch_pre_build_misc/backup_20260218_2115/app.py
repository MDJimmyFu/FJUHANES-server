from flask import Flask, render_template, request, jsonify
from his_client_final import HISClient
import datetime
import os
import sys
import json

# Ensure UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__, template_folder='templates', static_folder='static')
client = HISClient()

# Simple session-like storage for evaluation data (demo purposes)
EVAL_DATA_DIR = os.path.join(os.path.dirname(__file__), 'eval_data')
if not os.path.exists(EVAL_DATA_DIR):
    os.makedirs(EVAL_DATA_DIR)

@app.route('/')
def index():
    # Server-Side Rendering of Surgery List
    # Support 'date' (new standard) or 'bg_date' (legacy)
    date_param = request.args.get('date') or request.args.get('bg_date')
    if date_param:
        bg_date = date_param.replace('-', '')
    else:
        bg_date = datetime.datetime.now().strftime("%Y%m%d")
    try:
        surgeries = client.get_surgery_list(bg_date)
    except Exception as e:
        print(f"[-] SSR Error: {e}")
        surgeries = []
    
    return render_template('legacy_schedule.html', 
                           surgeries=surgeries, 
                           search_date=f"{bg_date[:4]}-{bg_date[4:6]}-{bg_date[6:]}")

@app.route('/patient_detail/<ordseq>')
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
        vitals_exm = client.get_vitals_from_exm(hhistnum, ordseq) or {}
        
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
            "vitals_exm": vitals_exm
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"[-] Detail Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/his/<method>', methods=['POST', 'GET'])
def his_proxy(method):
    try:
        # Support both GET params and POST form data
        params = request.args.to_dict() if request.method == 'GET' else request.form.to_dict()
        print(f"[*] Legacy API Call: {method} with params {params}")

        # Mapping of legacy methods to HISClient operations
        if method == 'getPatOperationList':
            date_str = params.get('pBGOPDATE', datetime.datetime.now().strftime("%Y%m%d"))
            data = client.get_surgery_list(date_str)
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
            return jsonify({"datastatus": 1, "returnList": full_data.get('INSPECTION_CXR', [])})

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
def get_surgery_list():
    try:
        data = request.get_json(silent=True) or {}
        # Support single date or range
        bg_date = data.get('bg_date', data.get('date', datetime.datetime.now().strftime("%Y%m%d"))).replace('-', '')
        end_date = data.get('end_date', bg_date).replace('-', '')
        
        print(f"[*] Fetching Surgery List from {bg_date} to {end_date}")
        # Note: HISClient.get_surgery_list currently only takes one date. 
        # For simplicity, if they are the same, just call once. 
        # If range, we might need a loop, but usually they query today.
        if bg_date == end_date:
            surgeries = client.get_surgery_list(bg_date)
        else:
            # Basic implementation for range: just fetch each day (expensive but correct if needed)
            # However, typically end_date is the same as bg_date for this app.
            surgeries = client.get_surgery_list(bg_date) 
            
        return jsonify(surgeries)
    except Exception as e:
        print(f"[-] Surgery List Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/details', methods=['POST'])
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
            results.update({
                "predata": pre_data,
                "lab_data": lab_data
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

if __name__ == '__main__':
    print("[*] Surgery Schedule Server Starting...")
    app.run(host='0.0.0.0', port=5000, debug=False)
