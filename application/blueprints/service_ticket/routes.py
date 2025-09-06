from flask import request, jsonify
from sqlalchemy import desc
from application.extensions import db, limiter
from application.models import ServiceTicket, Mechanic, Inventory
from application.schemas import ticket_schema, tickets_schema
from application.util import token_required
from . import ticket_bp


@ticket_bp.route("/", methods=["POST"])
@limiter.limit("10 per hour")
@token_required
def create_ticket(*, user_id, role):
    """
    ---
    tags: [Tickets]
    summary: Create ticket (auth)
    security: [{Bearer: []}]
    parameters:
      - in: body
        name: payload
        schema: { $ref: '#/definitions/TicketPayload' }
    responses:
      201: { description: Created, schema: { $ref: '#/definitions/TicketResponse' } }
      400: { description: Missing description, schema: { $ref: '#/definitions/ErrorResponse' } }
      401: { description: Unauthorized, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    data = request.get_json() or {}
    desc_ = data.get("description")
    if not desc_:
        return jsonify({"error": "description required"}), 400

    t = ServiceTicket(description=desc_, user_id=user_id)

    mid = data.get("primary_mechanic_id")
    if mid:
        mech = Mechanic.query.get(mid)
        if mech:
            t.primary_mechanic = mech

    db.session.add(t)
    db.session.commit()
    return ticket_schema.jsonify(t), 201


@ticket_bp.route("/", methods=["GET"])
@token_required
def list_tickets(*, user_id, role):
    """
    ---
    tags: [Tickets]
    summary: List tickets (auth)
    security: [{Bearer: []}]
    responses:
      200:
        description: OK
        schema:
          type: array
          items: { $ref: '#/definitions/TicketResponse' }
      401: { description: Unauthorized, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    rows = ServiceTicket.query.order_by(desc(ServiceTicket.id)).all()
    return jsonify(tickets_schema.dump(rows)), 200


@ticket_bp.route("/<int:tid>", methods=["GET"])
@token_required
def get_ticket(tid, *, user_id, role):
    """
    ---
    tags: [Tickets]
    summary: Get ticket by id (auth)
    security: [{Bearer: []}]
    responses:
      200: { description: OK, schema: { $ref: '#/definitions/TicketResponse' } }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    t = ServiceTicket.query.get_or_404(tid)
    return ticket_schema.jsonify(t), 200


@ticket_bp.route("/<int:tid>/edit", methods=["PUT"])
@token_required
def edit_mechanics(tid, *, user_id, role):
    """
    ---
    tags: [Tickets]
    summary: Add/Remove mechanics on a ticket (auth)
    description: Send lists of ids to add/remove.
    security: [{Bearer: []}]
    parameters:
      - in: body
        name: payload
        schema:
          type: object
          properties:
            add_ids:
              type: array
              items: { type: integer }
              example: [1,2]
            remove_ids:
              type: array
              items: { type: integer }
              example: [3]
    responses:
      200: { description: Updated, schema: { $ref: '#/definitions/TicketResponse' } }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    t = ServiceTicket.query.get_or_404(tid)
    data = request.get_json() or {}
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])

    if add_ids:
        for m in Mechanic.query.filter(Mechanic.id.in_(add_ids)).all():
            if m not in t.mechanics:
                t.mechanics.append(m)

    if remove_ids:
        t.mechanics = [m for m in t.mechanics if m.id not in set(remove_ids)]

    db.session.commit()
    return ticket_schema.jsonify(t), 200


@ticket_bp.route("/<int:tid>/add-part/<int:pid>", methods=["POST"])
@token_required
def add_part(tid, pid, *, user_id, role):
    """
    ---
    tags: [Tickets]
    summary: Add a part to a ticket (auth)
    security: [{Bearer: []}]
    responses:
      200: { description: OK, schema: { $ref: '#/definitions/TicketResponse' } }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    t = ServiceTicket.query.get_or_404(tid)
    p = Inventory.query.get_or_404(pid)
    if p not in t.parts:
        t.parts.append(p)
        db.session.commit()
    return ticket_schema.jsonify(t), 200


@ticket_bp.route("/<int:tid>", methods=["DELETE"])
@limiter.limit("10 per hour")
@token_required
def delete_ticket(tid, *, user_id, role):
    """
    ---
    tags: [Tickets]
    summary: Delete a ticket (auth)
    security: [{Bearer: []}]
    responses:
      200:
        description: Deleted
        schema:
          type: object
          properties:
            deleted: { type: integer, example: 7 }
      404: { description: Not found, schema: { $ref: '#/definitions/ErrorResponse' } }
    """
    t = ServiceTicket.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"deleted": tid}), 200
