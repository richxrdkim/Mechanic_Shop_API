from flask import request, jsonify
from sqlalchemy import desc
from application.extensions import db, limiter, cache
from application.models import Mechanic
from application.schemas import mechanic_schema, mechanics_schema
from application.util import token_required
from . import mechanic_bp


@mechanic_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def list_mechanics():
    """
    ---
    tags: [Mechanics]
    summary: List mechanics (public)
    responses:
      200:
        description: OK
        schema:
          type: array
          items: { $ref: '#/definitions/MechanicResponse' }
    """
    rows = Mechanic.query.order_by(desc(Mechanic.id)).all()
    return jsonify(mechanics_schema.dump(rows)), 200


@mechanic_bp.route("/<int:mid>", methods=["GET"])
def get_mechanic(mid):
    """
    ---
    tags: [Mechanics]
    summary: Get mechanic by id (public)
    responses:
      200: { description: OK, schema: { $ref: '#/definitions/MechanicResponse' } }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    m = Mechanic.query.get_or_404(mid)
    return mechanic_schema.jsonify(m), 200


@mechanic_bp.route("/", methods=["POST"])
@limiter.limit("10 per hour")
@token_required
def create_mechanic(*, user_id, role):
    """
    ---
    tags: [Mechanics]
    summary: Create mechanic (auth)
    security: [{Bearer: []}]
    parameters:
      - in: body
        name: payload
        schema: { $ref: '#/definitions/MechanicPayload' }
    responses:
      201: { description: Created, schema: { $ref: '#/definitions/MechanicResponse' } }
      400: { description: Missing name, schema: { $ref: '#/definitions/ErrorResponse' } }
      401: { description: Unauthorized, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name required"}), 400
    m = Mechanic(name=name)
    db.session.add(m)
    db.session.commit()
    return mechanic_schema.jsonify(m), 201


@mechanic_bp.route("/<int:mid>", methods=["PUT"])
@token_required
def update_mechanic(mid, *, user_id, role):
    """
    ---
    tags: [Mechanics]
    summary: Update mechanic (auth)
    security: [{Bearer: []}]
    parameters:
      - in: body
        name: payload
        schema:
          type: object
          properties:
            name: { type: string, example: "Casey Torque" }
    responses:
      200: { description: Updated, schema: { $ref: '#/definitions/MechanicResponse' } }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    m = Mechanic.query.get_or_404(mid)
    data = request.get_json() or {}
    if "name" in data:
        m.name = data["name"]
    db.session.commit()
    return mechanic_schema.jsonify(m), 200


@mechanic_bp.route("/<int:mid>", methods=["DELETE"])
@limiter.limit("10 per hour")
@token_required
def delete_mechanic(mid, *, user_id, role):
    """
    ---
    tags: [Mechanics]
    summary: Delete mechanic (auth)
    security: [{Bearer: []}]
    responses:
      200:
        description: Deleted
        schema:
          type: object
          properties:
            deleted: { type: integer, example: 2 }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    m = Mechanic.query.get_or_404(mid)
    db.session.delete(m)
    db.session.commit()
    return jsonify({"deleted": mid}), 200
