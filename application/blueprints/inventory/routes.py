from flask import request, jsonify
from application.extensions import db, limiter, cache
from application.models import Inventory
from application.utils.util import token_required, mechanic_token_required
from . import inventory_bp
from .schemas import inventory_schema, inventories_schema

# CREATE part (mechanic login optional-challenge; use token_required if you prefer)


@inventory_bp.route("/", methods=["POST"])
@limiter.limit("10 per hour")
@mechanic_token_required
def create_part(*, user_id, role):
    data = request.get_json() or {}
    part = inventory_schema.load(data)
    db.session.add(part)
    db.session.commit()
    return inventory_schema.jsonify(part), 201

# LIST parts (cached)


@inventory_bp.route("/", methods=["GET"])
@token_required
@cache.cached(timeout=60, query_string=True)
def list_parts(*, user_id, role):
    parts = Inventory.query.order_by(Inventory.name.asc()).all()
    return jsonify(inventories_schema.dump(parts)), 200

# GET one part


@inventory_bp.route("/<int:part_id>", methods=["GET"])
@token_required
def get_part(part_id, *, user_id, role):
    part = Inventory.query.get_or_404(part_id)
    return inventory_schema.jsonify(part), 200

# UPDATE part


@inventory_bp.route("/<int:part_id>", methods=["PUT"])
@mechanic_token_required
def update_part(part_id, *, user_id, role):
    part = Inventory.query.get_or_404(part_id)
    data = request.get_json() or {}
    if "name" in data:
        part.name = data["name"]
    if "price" in data:
        part.price = data["price"]
    db.session.commit()
    return inventory_schema.jsonify(part), 200

# DELETE part


@inventory_bp.route("/<int:part_id>", methods=["DELETE"])
@limiter.limit("10 per hour")
@mechanic_token_required
def delete_part(part_id, *, user_id, role):
    part = Inventory.query.get_or_404(part_id)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Part {part_id} deleted"}), 200
