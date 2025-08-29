from flask import Blueprint, request, jsonify
from application.models import Mechanic
from application.extensions import db
from .schemas import MechanicSchema

mechanic_bp = Blueprint("mechanic_bp", __name__)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

# CREATE


@mechanic_bp.route("/", methods=["POST"])
def add_mechanic():
    data = request.get_json() or {}
    mech = mechanic_schema.load(data)
    db.session.add(mech)
    db.session.commit()
    return mechanic_schema.jsonify(mech), 201

# READ all


@mechanic_bp.route("/", methods=["GET"])
def get_mechanics():
    mechs = Mechanic.query.all()
    return jsonify(mechanics_schema.dump(mechs)), 200

# READ one


@mechanic_bp.route("/<int:mechanic_id>", methods=["GET"])
def get_mechanic(mechanic_id):
    mech = Mechanic.query.get_or_404(mechanic_id)
    return mechanic_schema.jsonify(mech), 200

# UPDATE


@mechanic_bp.route("/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
    mech = Mechanic.query.get_or_404(mechanic_id)
    data = request.get_json() or {}
    for k, v in data.items():
        if hasattr(mech, k):
            setattr(mech, k, v)
    db.session.commit()
    return mechanic_schema.jsonify(mech), 200

# DELETE


@mechanic_bp.route("/<int:mechanic_id>", methods=["DELETE"])
def delete_mechanic(mechanic_id):
    mech = Mechanic.query.get_or_404(mechanic_id)
    db.session.delete(mech)
    db.session.commit()
    return jsonify({"message": f"Mechanic {mechanic_id} deleted"}), 200
