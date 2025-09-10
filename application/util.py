from functools import wraps
from datetime import datetime, timedelta
import jwt
from flask import request, jsonify, current_app


def make_token(user_id: int, role: str = "user") -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def token_required(fn):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth.split(" ", 1)[1]
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
        kwargs["user_id"] = data.get("sub")
        kwargs["role"] = data.get("role", "user")
        return fn(*args, **kwargs)
    return wrapper
