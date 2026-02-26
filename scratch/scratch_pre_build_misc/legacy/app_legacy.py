from flask import Flask, render_template, request, jsonify
from his_client_final import HISClient
import datetime
import os
import sys

# Ensure UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__, template_folder='templates', static_folder='static')
client = HISClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/surgery_list', methods=['POST'])
def get_surgery_list():
    try:
        # Frontend sends JSON: { date: "YYYY-MM-DD" } or similar
        # But original site used form data or JSON. Let's support JSON.
        data = request.get_json(silent=True) or {}
        date_str = data.get('date', '')
        
        # Format dateStr to YYYYMMDD
        if date_str:
            date_str = date_str.replace('-', '')
        else:
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            
        print(f"[*] API Request: Surgery List for {date_str}")
        surgeries = client.get_surgery_list(date_str)
        
        # Sort by room if possible, but frontend handles filtering.
        # Just return list.
        return jsonify(surgeries)

    except Exception as e:
        print(f"[-] API Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/details', methods=['POST'])
def get_details():
    try:
        data = request.get_json(silent=True) or {}
        ordseq = data.get('ordseq')
        hhistnum = data.get('hhistnum')
        section = data.get('section', 'all') # 'vitals', 'extended', or 'all'

        if not ordseq:
            return jsonify({"error": "Missing ordseq"}), 400

        results = {}
        
        # 1. Vitals/Labs (Phase 1)
        if section in ['vitals', 'all']:
            # For vitals, we need to activate first to ensure latest C430
            client.activate_patient(hhistnum)
            pre_data = client.get_pre_anesthesia_data(ordseq, hhistnum)
            lab_data = client.get_lab_data(hhistnum, ordseq, pre_data=pre_data)
            results.update({
                "predata": pre_data,
                "lab_data": lab_data
            })
            
        # 2. Extended Info (Phase 2)
        if section in ['extended', 'all']:
            charging_data = client.get_anesthesia_charging_data(ordseq, hhistnum) or {}
            results.update({
                "charging": charging_data
            })
            
        return jsonify(results)

    except Exception as e:
        print(f"[-] API Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("[*] Starting Flask Server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
