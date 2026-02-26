import requests
import json
import re
import time
import urllib.parse
import uuid
import os
from utils import get_resource_path

class HisClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url_80 = "http://10.10.246.80"
        self.base_url_179 = "http://10.10.245.179"
        self.cookie_80 = ""
        self.cookie_179 = ""

    def login(self, username, password):
        url = f"{self.base_url_80}/Ipo/HISLogin/CheckUserByID"
        data = {
            "signOnID": username,
            "signOnPassword": password
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-Requested-With": "XMLHttpRequest"
        }
        res = self.session.post(url, json=data, headers=headers)
        
        # Extract HIS_IPD cookie which contains user context
        if 'HIS_IPD' in self.session.cookies.get_dict():
            self.cookie_80 = self.session.cookies.get_dict()['HIS_IPD']
            return True, "Login successful"
        return False, f"Failed to get HIS_IPD cookie. Status: {res.status_code}, Body: {res.text[:100]}"

    def get_patients_by_ward(self, ward="11A"):
        url = f"{self.base_url_80}/Ipo/IpoQ222/GridData_Read"
        stamp_id = "03772"
        # Extract stampID from cookie if possible
        match = re.search(r"HISDrStampID=([^&]+)", self.cookie_80)
        if match:
            stamp_id = match.group(1)
            
        params = {"hNurstat": ward, "stampID": stamp_id}
        data = {"hNurSta": ward}
        res = self.session.post(url, params=params, data=data)
        try:
            return res.json().get('Data', [])
        except:
            return []

    def get_patient_by_chart(self, chart_no):
        # Step 1: Get HHISNum and HCaseNo
        url_ids = f"{self.base_url_80}/Ipo/IpoQ250/GetHHISNum"
        params = {"hHISNum": chart_no}
        headers = {"X-Requested-With": "XMLHttpRequest"}
        try:
            res_ids = self.session.get(url_ids, params=params, headers=headers)
            ids = res_ids.json()
            h_his_num = ids.get("HHISNum")
            h_case_no = ids.get("HCaseNo")
            
            if not h_his_num or not h_case_no:
                return {}
                
            # Step 2: Get full patient details
            url_refresh = f"{self.base_url_80}/Ipo/IpoC100/RefreshPatData"
            params_refresh = {"hHisNum": h_his_num, "hCaseNo": h_case_no}
            res_refresh = self.session.get(url_refresh, params=params_refresh, headers=headers)
            data = res_refresh.json()
            
            # Format data to match get_patients_by_ward format
            # Specifically, combine HNurSta and HBed if they are separate
            if data.get("HNurSta") and data.get("HBed"):
                data["HNurSta"] = f"{data['HNurSta']}-{data['HBed']}"
                
            return data
        except Exception:
            return {}

    def prescribe_package(self, patient_data, package_type="PCA"):
        h_case_no = patient_data.get("HCaseNo", "")
        h_his_num = patient_data.get("HHISNum") or patient_data.get("HChartNo") or patient_data.get("HChartno", "")
        nur_sta_full = patient_data.get("HNurSta") or patient_data.get("HDtl_No", "")
        # Extract base ward and bed from "TEST-044[3]" -> "TEST", "044"
        ward = nur_sta_full.split("-")[0] if "-" in nur_sta_full else nur_sta_full
        bed = nur_sta_full.split("-")[1].split("[")[0] if "-" in nur_sta_full else ""
        
        if not h_case_no or not h_his_num:
            return False, "Missing HCaseNo or HHISNum"

        # 1. CacheOrderData
        url_cache = f"{self.base_url_80}/Ipo/IpoC143/CacheOrderData"
        headers_json = {"Content-Type": "application/json; charset=UTF-8", "X-Requested-With": "XMLHttpRequest"}
        
        # Load base package from known working JSON
        try:
            painless_file = get_resource_path(os.path.join("Ipo", "basostds_painless.json"))
            with open(painless_file, "r", encoding="utf-8") as f:
                basostds = json.load(f)
        except Exception as e:
            return False, f"Failed to load package JSON template: {e}"

        record_id = str(uuid.uuid4()).upper()

        rx_keys = []
        tx_keys = []

        # Adjust for PCA vs Painless
        if package_type == "PCA":
            # Remove Ropica and adjust Fentanyl dose
            basostds = [item for item in basostds if item.get("OSTItem") != "ROP01"]
            for item in basostds:
                if item.get("OSTItem") == "FEN02":
                    item["Dose"] = 1.0
                    item["Route"] = "PCA"
                    item["OSTCode"] = "ANES_TEST1"
                    item["sKey"] = "A2ANES7ANES_TEST1" # Standardized PCA key based on pcap
                    rx_keys.append(item["sKey"])
                elif item.get("OSTItem", "").startswith("XTR"):
                    item["OSTCode"] = "ANES_TEST1"
                    item["sKey"] = f"A2ANES{item.get('OSTRecNo', '0')}ANES_TEST1"
                    tx_keys.append(item["sKey"])
        else:
            # For PAINLESS, just adjust OSTCode if needed, the template is already painless
            for item in basostds:
                item["OSTCode"] = "ANES-CC01"
                if item.get("OSTItem") == "FEN02" or item.get("OSTItem") == "ROP01":
                    rx_keys.append(item["sKey"])
                elif item.get("OSTItem", "").startswith("XTR"):
                    tx_keys.append(item["sKey"])

        # basostds array must contain stringified JSON items
        stringified_basostds = [json.dumps(item, separators=(',', ':')) for item in basostds]
        
        cache_payload = {
            "recordID": record_id,
            "hHISNum": h_his_num,
            "hCaseNo": h_case_no,
            "basostds": stringified_basostds
        }
        res_cache = self.session.post(url_cache, json=cache_payload, headers=headers_json)
        
        # 2. CacheOrderDataInput
        url_input = f"{self.base_url_80}/Ipo/IpoC143/CacheOrderDataInput"
        
        rx_codes_str = ",".join([f"'{k}'" for k in rx_keys])
        tx_codes_str = ",".join(tx_keys)
        
        input_payload = {
            "recordID": record_id,
            "hHISNum": h_his_num,
            "hCaseNo": h_case_no,
            "rxCodes": rx_codes_str,
            "txCodes": tx_codes_str,
            "dxCodes": "",
            "exmCodes": ""
        }
        res_input = self.session.post(url_input, json=input_payload, headers=headers_json)
        
        # 3. Modify the fetched items directly for IpoC11GSave
        headers_form = {"Content-Type": "application/x-www-form-urlencoded", "X-Requested-With": "XMLHttpRequest"}
        url_save = f"{self.base_url_80}/Ipo/IpoC11G/IpoC11GSave"
        
        try:
            sign_file = get_resource_path(os.path.join("Ipo", "fentanyl_sign_fixed.json"))
            with open(sign_file, "r", encoding="utf-8") as f:
                item_json = json.load(f)[0]
        except Exception as e:
            return False, f"Failed to load sign template: {e}"

        current_ms = int(time.time() * 1000)
        date_str = f"/Date({current_ms})/"

        # Update dynamic fields
        item_json["HHISTNum"] = None
        item_json["HNurSta"] = None
        item_json["HBedNo"] = None
        item_json["HcaseNo"] = None
        item_json["OrdBgnDTTM"] = date_str
        item_json["OrdEndDTTM"] = date_str
        item_json["UDOLasbillDate"] = date_str
        item_json["OrdSeq"] = None  # MUST be None for new prescription, "" causes 500
        item_json["UniqueID"] = str(uuid.uuid4()).upper()

        if package_type == "PAINLESS":
            item_json["UDOGivDose"] = 0.5
            item_json["UDDCmmDose"] = 0.5
            item_json["WDose"] = 0.5
            item_json["Dose"] = "0.5"
            item_json["UDOGivRoute"] = "PAINL"
            item_json["OrdProced"] = "Fentanyl 管二 高 0.5 mg/10 mL/Amp"
            item_json["Days"] = 0
        else:
            item_json["UDOGivDose"] = 1.0
            item_json["UDDCmmDose"] = 1.0
            item_json["WDose"] = 1.0
            item_json["Dose"] = "1.0"
            item_json["UDOGivRoute"] = "PCA"
            item_json["OrdProced"] = "Fentanyl 管二 高 1.0 mg/10 mL/Amp"
            item_json["Days"] = 1

        save_data = {
            "hHISNum": h_his_num,
            "hCaseNo": h_case_no,
            "ipoC11CViewsJson": json.dumps([item_json]),
            "keepOrdOEDrID": "",
            "setDrgCode": "ANES-CC01" if package_type == "PAINLESS" else "ANES_TEST1",
            "setDrgCodeYN": "",
            "RxControlJson": "[]"
        }
        
        res_save = self.session.post(url_save, data=save_data, headers=headers_form)
        
        print(f"IpoC11GSave HTTP {res_save.status_code}: {res_save.text[:500]}")
        if res_save.status_code == 200:
            return True, f"Prescription submitted successfully for {h_his_num}."
        else:
            error_details = res_save.text[:500]
            print(f"IpoC11GSave 500 Error:\n{error_details}")
            return False, f"Failed to submit: HTTP {res_save.status_code}. {error_details}"

    def get_latest_p022(self, h_case_no):
        url = f"{self.base_url_80}/Ipo/IpoC110/P022_Read"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest"}
        data = {
            "sort": "",
            "group": "",
            "filter": "",
            "hCaseNo": h_case_no,
            "uDOFunct": "ud"
        }
        
        try:
            res = self.session.post(url, data=data, headers=headers)
            print("P022_Read HTTP Code:", res.status_code)
            if res.status_code == 200:
                json_data = res.json()
                print("P022 json:", str(json_data)[:500])
                records = json_data.get("Data", [])
                if records:
                    # Sort by DrugTrackNo descending or just take the last element
                    records.sort(key=lambda x: x.get("DrugTrackNo", 0), reverse=True)
                    latest = records[0]
                    return latest.get("OrdSeq"), latest.get("DrugTrackNo")
        except Exception as e:
            print(f"Error fetching P022 list: {e}")
            
        return None, None

    def download_p022_pdf(self, h_case_no, drug_track_no, ord_seq):
        url_print = f"{self.base_url_80}/Ipo/IpoC110/PrintP022"
        
        # We can just use self.session which seamlessly manages ASP.NET_SessionId and HIS_IPD cookies on .80
        data = {
            "HCaseNo": h_case_no,
            "hPrintKind": "P022",
            "DrugTrackNo": drug_track_no,
            "OrdSeq": ord_seq
        }
        res = self.session.post(url_print, data=data, allow_redirects=True)
        html_report = res.text
        
        # Extract report source
        m = re.search(r'telerik_ReportViewer\((.*?)\)\s*;', html_report, re.DOTALL)
        if not m:
            return False, "Failed to extract telerik_ReportViewer data"
        
        try:
            cfg = json.loads(m.group(1))
            src = cfg['reportSource']
            if 'parameters' in src:
                src['parameterValues'] = src.pop('parameters')
            report_source_json = json.dumps(src)
        except Exception as e:
            return False, f"Failed parsing report source: {str(e)}"

        api_base = f"{self.base_url_80}/Ipo/api/reports"
        
        # 1. Register Client
        res_client = self.session.post(f"{api_base}/clients", json={"timeStamp": None})
        client_id = res_client.json().get('clientId')
        
        # 2. Create Instance
        res_inst = self.session.post(f"{api_base}/clients/{client_id}/instances", data=report_source_json, headers={"Content-Type": "application/json"})
        inst_id = res_inst.json().get('instanceId')
        
        # 3. Request Document
        res_doc = self.session.post(f"{api_base}/clients/{client_id}/instances/{inst_id}/documents", json={"format": "PDF", "deviceInfo": {}, "useCache": True})
        doc_id = res_doc.json().get('documentId')
        
        if not doc_id:
            return False, "Failed to get document ID"
            
        # 4. Download document
        doc_url = f"{api_base}/clients/{client_id}/instances/{inst_id}/documents/{doc_id}"
        for _ in range(15):
            res_pdf = self.session.get(doc_url)
            if res_pdf.status_code == 200:
                pdf_path = get_resource_path("Controlled_Drug_Sheet_P022.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(res_pdf.content)
                return True, pdf_path
            time.sleep(2)
            
        return False, "Timeout waiting for PDF generation"
