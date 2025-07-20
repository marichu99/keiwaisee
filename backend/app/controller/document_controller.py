from flask import Blueprint, jsonify, request
from app.utils.kra_pin_details import extract_taxpayer_details
from app.utils.police_clearance_details import extract_clearance_details
from app.utils.script import authenticate_kra_from_app
import os

document_bp = Blueprint('document', __name__)

@document_bp.route('/submit', methods=['POST'])
def submit():
    data = request.json
    kra_pin = data.get('kraPin')
    police_clearance = data.get('policeClearance')
    id_number = data.get('idNumber')

    res = authenticate_kra_from_app(kra_pin=kra_pin, police_number=police_clearance, id_number=id_number)
    print(f"the res is {res}")
    return jsonify({"success": res})

@document_bp.route('/extract_kra_pin', methods=['POST'])
def extract_kra_pin():
    file = request.files['file']
    file_path = file.filename
    file.save(file_path)

    try:
        extracted_details = extract_taxpayer_details(file_path)
        if "error" in extracted_details:
            return jsonify({"error": extracted_details["error"]})

        print(f"the extracted kra pin is {extracted_details['PIN']}")
        return jsonify({
            "kraPin": extracted_details["PIN"],
            "taxpayerName": extracted_details["Taxpayer Name"],
            "email": extracted_details["Email Address"]
        })
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@document_bp.route('/extract_police_clearance', methods=['POST'])
def extract_police_clearance():
    file = request.files['file']
    file_path = file.filename
    file.save(file_path)

    try:
        extracted_details = extract_clearance_details(file_path)
        if "error" in extracted_details:
            return jsonify({"error": extracted_details["error"]})

        ref_no = extracted_details["Reference Number"]
        id_no = extracted_details["ID Number"]
        print(f"the extracted police clearance is {ref_no}")
        return jsonify({"refNo": ref_no, "idNo": id_no})
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@document_bp.route('/test', methods=['GET'])
def test_imports():
    try:
        import playwright.sync_api
        from PIL import Image
        import pytesseract
        return jsonify({"message": "All imports work!"})
    except ImportError as e:
        return jsonify({"error": str(e)}), 500