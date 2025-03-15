from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
import os

# Secret key for JWT
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if 'Authorization' header is present
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']

            # The token is expected to be in the format "Bearer <token>"
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Verify the token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['sub']  # 'sub' is the identity we stored in the token
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        # Pass the decoded information to the decorated function
        return f(current_user, *args, **kwargs)

    return decorated