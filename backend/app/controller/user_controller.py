from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.model.user import User
from app import db,bcrypt
from datetime import datetime

user_bp = Blueprint('user', __name__)

# Get all users (protected)
@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    current_user_id = get_jwt_identity()
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone_number': user.phone_number,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None
    } for user in users])

# Get a single user by ID (protected)
@user_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone_number': user.phone_number,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None
    })

# Create a new user
@user_bp.route('/', methods=['POST'])
def create_user():
    form_data = request.get_json()
    print(f"the data is {form_data}")
    data = form_data.get('formData')
    if not data:
        return jsonify({'error': 'Missing formData'}), 400
    required_fields = ['username', 'email', 'password']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Username, email, and password are required'}), 400

    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Username or email already exists'}), 400
    if data.get('phone_number') and User.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'error': 'Phone number already exists'}), 400

    # Parse date_of_birth if provided
    date_of_birth = None
    if data.get('dateOfBirth'):
        try:
            date_of_birth = datetime.fromisoformat(data['dateOfBirth']).date()
        except ValueError:
            return jsonify({'error': 'Invalid dateOfBirth format. Use YYYY-MM-DD'}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        phone_number=data.get('phoneNumber'),
        date_of_birth=date_of_birth
    )
    db.session.add(user)
    db.session.commit()

    # Generate JWT token for auto-login
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone_number': user.phone_number,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
        'access_token': access_token,
        'message': 'User created successfully'
    }), 201

# Update a user (protected)
@user_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(id)
    if user.id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.phone_number = data.get('phone_number', user.phone_number)
    if data.get('date_of_birth'):
        try:
            user.date_of_birth = datetime.fromisoformat(data['date_of_birth']).date()
        except ValueError:
            return jsonify({'error': 'Invalid date_of_birth format. Use YYYY-MM-DD'}), 400
    if data.get('password'):
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    db.session.commit()
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone_number': user.phone_number,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None
    })

# Delete a user (protected)
@user_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(id)
    if user.id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 204

# Login route
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'access_token': access_token,
            'message': 'Login successful'
        }), 200
    return jsonify({'error': 'Invalid username or password'}), 401
    
@user_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'username': user.username,
        'id': user.id,
        'email': user.email,
        'phone_number': user.phone_number,
        'date_of_birth': str(user.date_of_birth) if user.date_of_birth else None
    }), 200