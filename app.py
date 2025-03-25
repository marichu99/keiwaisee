from flask import Flask, render_template, request, jsonify
from kra_pin_details import extract_taxpayer_details
import mpesa_service
from police_clearance_details import extract_clearance_details
from flask_cors import CORS
import subprocess
import os
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Route to serve the HTML form
@app.route('/')
def home():
    return render_template('index.html') 

# Endpoint to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    kra_pin = data.get('kraPin')
    police_clearance = data.get('policeClearance')
    id_number = data.get('idNumber')

    print(sys.executable)
    print(sys.path)


    # Run the Playwright script as a subprocess
    env = os.environ.copy()
    env['PYTHONPATH'] = 'C:\\Users\\h\\Documents\\Projects\\keiwaisee\\myenv\\lib\\site-packages'

    process = subprocess.Popen(
        ["python", "script.py", kra_pin, police_clearance, id_number],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    stdout, stderr = process.communicate()

    # Return the output back to the client
    if process.returncode == 0:
        return jsonify({"message": "Success", "output": stdout})
    else:
        return jsonify({"message": "Error", "error": stderr}), 500
    
@app.route('/extract_kra_pin', methods=['POST'])
def extract_pin():
    file = request.files['file']
    
    # Temporary save the uploaded file
    file_path = f"{file.filename}"
    file.save(file_path)

    # Extract KRA PIN from PDF
    extracted_kra_pin = extract_taxpayer_details(file_path)["PIN"]

    print(f"the extracted kra pin is {extracted_kra_pin} ")

    return jsonify({"kraPin": extracted_kra_pin})

# Flask routes for testing 
@app.route("/stkpush/<phone>/<amount>", methods=["GET"])
def stk_push(phone, amount):
    mpesa = mpesa_service.MpesaService()
    response = mpesa.stk_push_simulation(phone, int(amount))
    return jsonify(response)

@app.route('/extract_police_clearance', methods=['POST'])
def extract_police_clearance():
    file = request.files['file']
    
    # Temporary save the uploaded file
    file_path = f"{file.filename}"
    file.save(file_path)

    # Extract KRA PIN from PDF
    extract_police_clearance = extract_clearance_details(file_path)["Reference Number"]
    extract_id_number = extract_clearance_details(file_path)["ID Number"]

    print(f"the extracted police clearance is {extract_police_clearance} ")

    return jsonify({"refNo": extract_police_clearance, "idNo":extract_id_number})

@app.route('/test')
def test_imports():
    try:
        import playwright.sync_api
        from PIL import Image
        import pytesseract
        return "All imports work!"
    except ImportError as e:
        return str(e)
    
@app.route("/path", methods=["POST"])
def path():
    mpesa = mpesa_service.MpesaService()
    data = request.get_json()
    checkout_request_id = data.get("checkoutRequestID")
    token = data.get("token")

    if not checkout_request_id or not token:
        return jsonify({"error": "Missing required parameters"}), 400

    response = mpesa.path(checkout_request_id, token)
    return jsonify(response)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=False)
