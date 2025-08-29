import jwt
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from functools import wraps


def encode_token(user_id):
    """Generate JWT token with 1-hour expiry"""
    payload = {
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "sub": user_id
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token):
    """Decode a JWT token and return user_id or error string"""
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload["sub"]   # user_id
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Invalid token"


def token_required(f):
    """Decorator to protect routes with JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Look for token in the Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        user_id = decode_token(token)
        if isinstance(user_id, str):  # If it's an error message
            return jsonify({"message": user_id}), 401

        # Pass user_id into route if needed
        return f(user_id=user_id, *args, **kwargs)

    return decorated
