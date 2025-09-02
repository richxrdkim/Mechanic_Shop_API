
from functools import wraps
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, current_app
from jose import jwt, JWTError


def encode_token(user_id: int, role: str = "user", expires_in: int | None = None) -> str:
    secret = current_app.config["SECRET_KEY"]
    if expires_in is None:
        expires_in = current_app.config.get("TOKEN_EXPIRES_IN", 3600)
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _extract_bearer() -> str | None:
    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        return None
    return auth.split(" ", 1)[1].strip()


def _decode_token_or_401(token: str) -> dict | None:
    secret = current_app.config["SECRET_KEY"]
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError:
        return None


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_bearer()
        if not token:
            return jsonify({"error": "Authorization header missing or invalid"}), 401
        payload = _decode_token_or_401(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        kwargs["user_id"] = int(payload.get("sub", 0))
        kwargs["role"] = payload.get("role", "user")
        return fn(*args, **kwargs)
    return wrapper
