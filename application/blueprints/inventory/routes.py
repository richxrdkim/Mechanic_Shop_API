from flask import request, jsonify
from sqlalchemy import asc
from application.extensions import db, limiter, cache
from application.models import Inventory
from application.schemas import inventory_schema, inventories_schema
from application.util import token_required
from . import inventory_bp

# CREATE


@inventory_bp.route("/", methods=["POST"])
@limiter.limit("10 per hour")
@token_required
def create_part(*, user_id, role):
    data = request.get_json() or {}
    name = data.get("name")
    price = data.get("price")
    if not name or price is None:
        return jsonify({"error": "name and price are required"}), 400
    part = Inventory(name=name, price=price)
    db.session.add(part)
    db.session.commit()
    return inventory_schema.jsonify(part), 201

# LIST (cached)


@inventory_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def list_parts():
    parts = Inventory.query.order_by(asc(Inventory.name)).all()
    return jsonify(inventories_schema.dump(parts)), 200

# READ


@inventory_bp.route("/<int:pid>", methods=["GET"])
def get_part(pid):
    part = Inventory.query.get_or_404(pid)
    return inventory_schema.jsonify(part), 200

# UPDATE


@inventory_bp.route("/<int:pid>", methods=["PUT"])
@token_required
def update_part(pid, *, user_id, role):
    part = Inventory.query.get_or_404(pid)
    data = request.get_json() or {}
    if "name" in data:
        part.name = data["name"]
    if "price" in data:
        part.price = data["price"]
    db.session.commit()
    return inventory_schema.jsonify(part), 200

# DELETE


@inventory_bp.route("/<int:pid>", methods=["DELETE"])
@limiter.limit("10 per hour")
@token_required
def delete_part(pid, *, user_id, role):
    part = Inventory.query.get_or_404(pid)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"deleted": pid}), 200
