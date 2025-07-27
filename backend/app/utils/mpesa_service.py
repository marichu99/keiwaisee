import os
import base64
import time
import requests
from flask import Flask, jsonify
from flask_jwt_extended import get_jwt_identity,jwt_required
from dotenv import load_dotenv
from app.model.payment import Payment
from app import db
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)

class MpesaService:
    def __init__(self):
        self.api_url = os.getenv("MPESA_API_URL")
        self.app_key_secret = os.getenv("MPESA_APP_KEY_SECRET")
        self.shortcode = os.getenv("MPESA_BUSINESS_SHORTCODE")
        self.passkey = os.getenv("MPESA_PASSKEY")
        self.callback_url = os.getenv("MPESA_CALLBACK_URL")

    def authenticate(self):
        """Authenticate with Safaricom API and return an access token."""
        print("we are now authenticating >>>>>>>")
        encoded_key = base64.b64encode(self.app_key_secret.encode()).decode()
        url = f"{self.api_url}/oauth/v1/generate?grant_type=client_credentials"
        print(f"The url is {url}")        

        headers = {"Authorization": f"Basic {encoded_key}"}
        response = requests.get(url, headers=headers, verify=False)

        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise Exception(f"Error getting access token: {response.text}")

    def generate_password(self, timestamp):
        """Generate Base64 encoded password for authentication."""
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_str.encode()).decode()

    def stk_push_simulation(self, phone_number, amount,user_id):
        """Initiate an STK Push request."""
        token = self.authenticate()
        url = f"{self.api_url}/mpesa/stkpush/v1/processrequest"

        timestamp = time.strftime("%Y%m%d%H%M%S")
        password = self.generate_password(timestamp)

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PhoneNumber": phone_number,
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "CallBackURL": self.callback_url,
            "AccountReference": "Test123",
            "TransactionDesc": "Payment for services",
        }

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)

        response_data = response.json()
        print(f"the response data obtained is {response_data}")
        checkout_request_id = response_data.get("CheckoutRequestID")

        if checkout_request_id:
            time.sleep(8)
            success = self.call_path_recursively(checkout_request_id, token,phone_number,amount,user_id)
            print(f"The transaction sucess {success}")
            print(f"The transaction sucess {int(success)}")
            if(int(success) == 0):
                return "Transaction completed successfully."
            else:
                return "Transaction failed."

        return response_data

    def call_path_recursively(self, checkout_request_id, token,phone_number,amount,user_id):
        """Check STK push status recursively until completed."""
        time.sleep(3)
        response = self.path(checkout_request_id, token)

        error_code = response.get("errorCode")
        if error_code:
            self.call_path_recursively(checkout_request_id, token)

        result_code = response.get("ResultCode")
        result_desc = response.get("ResultDesc", "Unknown error")

        print(f"The result obtained is {response}")

        if result_code == "0":
            print("Transaction completed successfully.")
            payment = Payment(
                user_id=user_id,
                phone_number=phone_number,
                amount=amount,    
                result_desc=result_desc,    
                reference_code=f"PAY-{uuid.uuid4().hex[:10].upper()}"
            )
            db.session.add(payment)
            db.session.commit()
            return result_code
        else:
            print(f"Transaction failed: {result_desc}")
            payment = Payment(
                user_id=user_id,
                phone_number=phone_number,
                amount=amount,    
                result_desc=result_desc,    
                reference_code=f"PAY-FAILED"
            )
            db.session.add(payment)
            db.session.commit()
            return result_code

    def path(self, checkout_request_id, token):
        """Query STK push transaction status."""
        url = f"{self.api_url}/mpesa/stkpushquery/v1/query"

        timestamp = time.strftime("%Y%m%d%H%M%S")
        password = self.generate_password(timestamp)

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)

        return response.json()



if __name__ == "__main__":
    app.run(debug=True)
