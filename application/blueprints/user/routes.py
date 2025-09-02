from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import asc
from application.extensions import db, limiter, cache
from application.models import User, ServiceTicket
from application.schemas import user_schema, users_schema, login_schema, tickets_schema
from application.util import encode_token, token_required
from . import user_bp

# CREATE (signup) -> returns token


@user_bp.route("/", methods=["POST"])
@limiter.limit("5 per hour")
def add_user():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409

    user = User(name=name, email=email,
                password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    token = encode_token(user.id, role="user")
    payload = user_schema.dump(user)
    payload["token"] = token
    return jsonify(payload), 201

# LOGIN -> returns token


@user_bp.route("/login", methods=["POST"])
@limiter.limit("10 per hour")
def login():
    data = request.get_json() or {}
    errors = login_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "invalid credentials"}), 401

    token = encode_token(user.id, role="user")
    return jsonify({"token": token, "user": user_schema.dump(user)}), 200

# LIST (paginated, cached)


@user_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
@token_required
def get_users(*, user_id, role):
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 10)), 1), 100)

    q = User.query.order_by(asc(User.name))
    paginated = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": users_schema.dump(paginated.items),
        "page": page,
        "per_page": per_page,
        "total": paginated.total,
        "pages": paginated.pages
    }), 200

# READ one


@user_bp.route("/<int:uid>", methods=["GET"])
@token_required
def get_user(uid, *, user_id, role):
    user = User.query.get_or_404(uid)
    return user_schema.jsonify(user), 200

# UPDATE (self or admin)


@user_bp.route("/<int:uid>", methods=["PUT"])
@token_required
def update_user(uid, *, user_id, role):
    if user_id != uid and role != "admin":
        return jsonify({"error": "forbidden"}), 403

    user = User.query.get_or_404(uid)
    data = request.get_json() or {}
    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        if User.query.filter(User.email == data["email"], User.id != uid).first():
            return jsonify({"error": "email already in use"}), 409
        user.email = data["email"]
    if "password" in data and data["password"]:
        user.password_hash = generate_password_hash(data["password"])

    db.session.commit()
    return user_schema.jsonify(user), 200

# DELETE (self or admin)


@user_bp.route("/<int:uid>", methods=["DELETE"])
@token_required
def delete_user(uid, *, user_id, role):
    if user_id != uid and role != "admin":
        return jsonify({"error": "forbidden"}), 403
    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"deleted": uid}), 200

# My tickets (auth)


@user_bp.route("/my-tickets", methods=["GET"])
@token_required
def my_tickets(*, user_id, role):
    tickets = ServiceTicket.query.filter_by(user_id=user_id).all()
    return jsonify(tickets_schema.dump(tickets)), 200
