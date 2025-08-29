from flask import Blueprint, request, jsonify
from application.models import User
from application.extensions import db, limiter, cache
from .schemas import UserSchema
from application.utils.util import encode_token, token_required

user_bp = Blueprint("user_bp", __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# CREATE (returns token)


@user_bp.route("/", methods=["POST"])
@limiter.limit("5 per hour")
def add_user():
    data = request.get_json() or {}
    user = user_schema.load(data)
    db.session.add(user)
    db.session.commit()

    token = encode_token(user.id)
    return jsonify({"user": user_schema.dump(user), "token": token}), 201


# READ all (Protected)
@user_bp.route("/", methods=["GET"])
@token_required
@cache.cached(timeout=60)
def get_users(user_id):
    users = User.query.all()
    return jsonify(users_schema.dump(users)), 200


# READ one (Protected)
@user_bp.route("/<int:user_id>", methods=["GET"])
@token_required
def get_user(user_id, **kwargs):
    user = User.query.get_or_404(user_id)
    return user_schema.jsonify(user), 200


# UPDATE (Protected)
@user_bp.route("/<int:user_id>", methods=["PUT"])
@token_required
def update_user(user_id, **kwargs):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    for k, v in data.items():
        if hasattr(user, k):
            setattr(user, k, v)
    db.session.commit()
    return user_schema.jsonify(user), 200


# DELETE (Protected)
@user_bp.route("/<int:user_id>", methods=["DELETE"])
@limiter.limit("5 per hour")
@token_required
def delete_user(user_id, **kwargs):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {user_id} deleted"}), 200
