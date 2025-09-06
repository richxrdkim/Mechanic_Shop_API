from flask import request, jsonify
from sqlalchemy import desc
from application.extensions import db, limiter, cache
from application.models import Inventory
from application.schemas import inventory_schema, inventories_schema
from application.util import token_required
from . import inventory_bp


@inventory_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def list_parts():
    """
    ---
    tags: [Inventory]
    summary: List parts (public)
    responses:
      200:
        description: OK
        schema:
          type: array
          items: { $ref: '#/definitions/InventoryResponse' }
    """
    rows = Inventory.query.order_by(desc(Inventory.id)).all()
    return jsonify(inventories_schema.dump(rows)), 200


@inventory_bp.route("/<int:pid>", methods=["GET"])
def get_part(pid):
    """
    ---
    tags: [Inventory]
    summary: Get part by id (public)
    responses:
      200: { description: OK, schema: { $ref: '#/definitions/InventoryResponse' } }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    p = Inventory.query.get_or_404(pid)
    return inventory_schema.jsonify(p), 200


@inventory_bp.route("/", methods=["POST"])
@limiter.limit("10 per hour")
@token_required
def create_part(*, user_id, role):
    """
    ---
    tags: [Inventory]
    summary: Create part (auth)
    security: [{Bearer: []}]
    parameters:
      - in: body
        name: payload
        schema: { $ref: '#/definitions/InventoryPayload' }
    responses:
      201: { description: Created, schema: { $ref: '#/definitions/InventoryResponse' } }
      400: { description: Missing name, schema: { $ref: '#/definitions/ErrorResponse' } }
      401: { description: Unauthorized, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name required"}), 400
    p = Inventory(name=name)
    db.session.add(p)
    db.session.commit()
    return inventory_schema.jsonify(p), 201


@inventory_bp.route("/<int:pid>", methods=["PUT"])
@token_required
def update_part(pid, *, user_id, role):
    """
    ---
    tags: [Inventory]
    summary: Update part (auth)
    security: [{Bearer: []}]
    parameters:
      - in: body
        name: payload
        schema:
          type: object
          properties:
            name: { type: string, example: "Oil Filter XL" }
    responses:
      200: { description: Updated, schema: { $ref: '#/definitions/InventoryResponse' } }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    p = Inventory.query.get_or_404(pid)
    data = request.get_json() or {}
    if "name" in data:
        p.name = data["name"]
    db.session.commit()
    return inventory_schema.jsonify(p), 200


@inventory_bp.route("/<int:pid>", methods=["DELETE"])
@limiter.limit("10 per hour")
@token_required
def delete_part(pid, *, user_id, role):
    """
    ---
    tags: [Inventory]
    summary: Delete part (auth)
    security: [{Bearer: []}]
    responses:
      200:
        description: Deleted
        schema:
          type: object
          properties:
            deleted: { type: integer, example: 5 }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    p = Inventory.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"deleted": pid}), 200
