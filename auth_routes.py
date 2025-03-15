from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime

auth_bp = Blueprint('auth', __name__)

# Hardcoded admin credentials for demonstration
# In a real application, these would be stored in a database with hashed passwords
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'


@auth_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    # Check if credentials match the hardcoded admin credentials
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create a JWT token
        access_token = create_access_token(
            identity=username,
            expires_delta=datetime.timedelta(hours=1)
        )
        return jsonify({"message": "Login successful", "token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401


@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"logged_in_as": current_user}), 200