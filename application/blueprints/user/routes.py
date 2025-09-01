from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from application.extensions import db, limiter, cache
from application.models import User, ServiceTicket
from application.utils.util import token_required, encode_token
from . import user_bp
from .schemas import user_schema, users_schema, login_schema

# CREATE user (rate-limited)


@user_bp.route("/", methods=["POST"])
@limiter.limit("5 per hour")
def create_user():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not all([name, email, password]):
        return jsonify({"error": "name, email, password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already exists"}), 400

    u = User(name=name, email=email,
             password_hash=generate_password_hash(password))
    db.session.add(u)
    db.session.commit()

    # Optional: return a token on signup (nice for testing)
    token = encode_token(u.id, role="user")
    return jsonify({"user": user_schema.dump(u), "token": token}), 201

# LOGIN -> returns token


@user_bp.route("/login", methods=["POST"])
@limiter.limit("10 per hour")
def login():
    data = request.get_json() or {}
    errors = login_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.password_hash or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    token = encode_token(user.id, role="user")
    return jsonify({"token": token, "user": user_schema.dump(user)}), 200

# GET users (paginated + cached + token)


@user_bp.route("/", methods=["GET"])
@token_required
@cache.cached(timeout=60, query_string=True)
def get_users(*, user_id, role):
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = max(1, min(int(request.args.get("per_page", 10)), 100))
    except ValueError:
        page, per_page = 1, 10
    pagination = User.query.order_by(User.id.asc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "items": users_schema.dump(pagination.items)
    }), 200

# GET my tickets (token required)


@user_bp.route("/my-tickets", methods=["GET"])
@token_required
def my_tickets(*, user_id, role):
    tickets = ServiceTicket.query.filter_by(user_id=user_id).all()
    # avoid circular import
    from application.blueprints.service_ticket.schemas import tickets_schema
    return jsonify(tickets_schema.dump(tickets)), 200
