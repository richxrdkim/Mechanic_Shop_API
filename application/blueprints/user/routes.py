from flask import Blueprint, request, jsonify
from application.models import User
from application.extensions import db
from .schemas import UserSchema

user_bp = Blueprint("user_bp", __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# CREATE


@user_bp.route("/", methods=["POST"])
def add_user():
    data = request.get_json() or {}
    user = user_schema.load(data)
    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user), 201

# READ all


@user_bp.route("/", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users)), 200

# READ one


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return user_schema.jsonify(user), 200

# UPDATE


@user_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    for k, v in data.items():
        if hasattr(user, k):
            setattr(user, k, v)
    db.session.commit()
    return user_schema.jsonify(user), 200

# DELETE


@user_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {user_id} deleted"}), 200
