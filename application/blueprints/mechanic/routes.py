from flask import Blueprint, request, jsonify
from application.models import Mechanic
from application.extensions import db, limiter, cache
from .schemas import MechanicSchema
from app.utils.util import token_required  # <-- add this

mechanic_bp = Blueprint("mechanic_bp", __name__)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

# CREATE (Protected)


@mechanic_bp.route("/", methods=["POST"])
@limiter.limit("5 per hour")
@token_required
def add_mechanic(*, user_id):
    data = request.get_json() or {}
    mech = mechanic_schema.load(data)
    db.session.add(mech)
    db.session.commit()
    return mechanic_schema.jsonify(mech), 201

# READ all (Protected + Cached after auth)


@mechanic_bp.route("/", methods=["GET"])
@token_required
@cache.cached(timeout=60)
def get_mechanics(*, user_id):
    mechs = Mechanic.query.all()
    return jsonify(mechanics_schema.dump(mechs)), 200

# READ one (Protected)


@mechanic_bp.route("/<int:mechanic_id>", methods=["GET"])
@token_required
def get_mechanic(mechanic_id, *, user_id):
    mech = Mechanic.query.get_or_404(mechanic_id)
    return mechanic_schema.jsonify(mech), 200

# UPDATE (Protected)


@mechanic_bp.route("/<int:mechanic_id>", methods=["PUT"])
@token_required
def update_mechanic(mechanic_id, *, user_id):
    mech = Mechanic.query.get_or_404(mechanic_id)
    data = request.get_json() or {}
    for k, v in data.items():
        if hasattr(mech, k):
            setattr(mech, k, v)
    db.session.commit()
    return mechanic_schema.jsonify(mech), 200

# DELETE (Protected + rate limited)


@mechanic_bp.route("/<int:mechanic_id>", methods=["DELETE"])
@limiter.limit("5 per hour")
@token_required
def delete_mechanic(mechanic_id, *, user_id):
    mech = Mechanic.query.get_or_404(mechanic_id)
    db.session.delete(mech)
    db.session.commit()
    return jsonify({"message": f"Mechanic {mechanic_id} deleted"}), 200
