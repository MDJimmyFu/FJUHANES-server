from flask import Flask, request, jsonify, send_file, render_template, session
from his_client import HisClient
from utils import get_resource_path
import os
import requests
import uuid

app = Flask(__name__, 
            template_folder=get_resource_path('AutoPrescribe/templates'),
            static_folder=get_resource_path('AutoPrescribe/static'))

app.secret_key = os.urandom(24) # Set a random secret key for session

def get_client():
    if 'his_cookies' not in session:
        return None
    req_session = requests.Session()
    req_session.cookies.update(session['his_cookies'])
    
    client = HisClient(session=req_session)
    if 'HIS_IPD' in session['his_cookies']:
        client.cookie_80 = session['his_cookies']['HIS_IPD']
    return client

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    client = HisClient()
    success, msg = client.login(data.get('username'), data.get('password'))
    
    if success:
        session['his_cookies'] = client.session.cookies.get_dict()
        
    return jsonify({"success": success, "message": msg})

@app.route('/api/patients', methods=['GET'])
def get_patients():
    client = get_client()
    if not client:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    ward = request.args.get('ward', '11A')
    chart_no = request.args.get('chartNo', '')

    if chart_no:
        data = client.get_patient_by_chart(chart_no)
        # Wrap single patient into list for consistent frontend format
        if isinstance(data, dict) and data.get("HHISNum"):
            return jsonify({"success": True, "data": [data]})
        else:
            return jsonify({"success": True, "data": []})
    else:
        patients = client.get_patients_by_ward(ward)
        return jsonify({"success": True, "data": patients})

@app.route('/api/prescribe', methods=['POST'])
def prescribe():
    client = get_client()
    if not client:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    data = request.json
    patient_data = data.get('patient')
    package_type = data.get('packageType') # 'PCA' or 'PAINLESS'

    if not patient_data or not package_type:
        return jsonify({"success": False, "message": "Missing patient data or package type"})
    
    # 1. Execute prescription
    if package_type == 'INTUBATION' or package_type == 'INTUBATION_INF':
        is_inf = (package_type == 'INTUBATION_INF')
        success, msg = client.prescribe_intubation(patient_data, infection=is_inf)
        if success:
            return jsonify({"success": True, "message": msg})
        else:
            return jsonify({"success": False, "message": f"Prescription failed: {msg}"})

    success, msg = client.prescribe_package(patient_data, package_type)
    if not success:
        return jsonify({"success": False, "message": f"Prescription failed: {msg}"})

    # Automatically prescribe vital sign orders for Painless Labor
    if package_type == 'PAINLESS':
        v_success, v_msg = client.prescribe_painless_vitals(patient_data)
        if not v_success:
            print(f"Warning: Painless vital signs failed: {v_msg}")
        else:
            print("Painless vital signs submitted successfully.")

    # 2. Extract OrdSeq and DrugTrackNo for PDF
    h_case_no = patient_data.get("HCaseNo")
    
    # Wait briefly for HIS to commit the prescription
    import time
    time.sleep(2)
    
    ord_seq, drug_track_no = client.get_latest_p022(h_case_no)
    
    if not ord_seq or not drug_track_no:
        return jsonify({"success": False, "message": "Prescription signed, but failed to find the generated Controlled Drug Sheet."})

    # 3. Download PDF
    pdf_success, pdf_msg = client.download_p022_pdf(h_case_no, drug_track_no, ord_seq)
    
    if pdf_success:
        # pdf_msg contains the random filename 
        return jsonify({"success": True, "message": "Flow complete", "pdfUrl": f"/api/download_pdf?file={pdf_msg}"})
    else:
        return jsonify({"success": False, "message": f"PDF download failed: {pdf_msg}"})

@app.route('/api/download_pdf')
def download_pdf():
    file_name = request.args.get("file")
    if not file_name or not file_name.endswith('.pdf'):
        return "Invalid file request", 400
    # Resolve file path relative to this script's directory for portability
    file_path = get_resource_path(os.path.join('AutoPrescribe', file_name))
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=False)
    return f"File not found: {file_name}", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
