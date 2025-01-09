from flask import Flask, render_template, request, jsonify
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

@app.route('/test')
def test_imports():
    try:
        import playwright.sync_api
        from PIL import Image
        import pytesseract
        return "All imports work!"
    except ImportError as e:
        return str(e)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=False)
