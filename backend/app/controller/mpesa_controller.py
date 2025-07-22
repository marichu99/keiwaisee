from flask import Blueprint, jsonify, request
from app.utils.mpesa_service import MpesaService

mpesa_bp = Blueprint('mpesa', __name__)

@mpesa_bp.route('/stkpush', methods=['POST'])
def stkpush():
    data = request.get_json()
    phone = data.get('phone_number')
    amount = data.get('amount')
    mpesa = MpesaService()
    response = mpesa.stk_push_simulation(phone, int(amount))
    return jsonify(response)

@mpesa_bp.route('/path', methods=['POST'])
def path():
    mpesa = MpesaService()
    data = request.get_json()
    checkout_request_id = data.get('checkoutRequestID')
    token = data.get('token')

    if not checkout_request_id or not token:
        return jsonify({"error": "Missing required parameters"}), 400

    response = mpesa.path(checkout_request_id, token)
    return jsonify(response)