from functools import wraps
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, current_app
from jose import jwt, JWTError


def encode_token(user_id: int, role: str = "user", expires_in: int | None = None) -> str:
    """
    Create a JWT for a user (or mechanic when role='mechanic').
    """
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


def _decode_token_or_401(token: str):
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def _extract_bearer():
    hdr = request.headers.get("Authorization", "")
    if not hdr.startswith("Bearer "):
        return None
    return hdr.split(" ", 1)[1].strip()


def token_required(fn):
    """
    Validates Bearer token. Injects user_id and role into the route as keyword-only args.
    """
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


def mechanic_token_required(fn):
    """
    Optional-challenge: requires a token with role="mechanic".
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_bearer()
        if not token:
            return jsonify({"error": "Authorization header missing or invalid"}), 401
        payload = _decode_token_or_401(token)
        if not payload or payload.get("role") != "mechanic":
            return jsonify({"error": "Mechanic authorization required"}), 403
        kwargs["user_id"] = int(payload.get("sub", 0))
        kwargs["role"] = "mechanic"
        return fn(*args, **kwargs)
    return wrapper
