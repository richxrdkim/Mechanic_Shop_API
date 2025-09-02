from flask import request, jsonify
from sqlalchemy import desc
from application.extensions import db, limiter, cache
from application.models import ServiceTicket, Mechanic, Inventory
from application.schemas import ticket_schema, tickets_schema
from application.util import token_required
from . import ticket_bp

# CREATE


@ticket_bp.route("/", methods=["POST"])
@limiter.limit("10 per hour")
@token_required
def create_ticket(*, user_id, role):
    data = request.get_json() or {}
    desc_ = data.get("description")
    if not desc_:
        return jsonify({"error": "description is required"}), 400

    t = ServiceTicket(description=desc_, user_id=user_id)

    # optional primary mechanic
    mid = data.get("primary_mechanic_id")
    if mid:
        mech = Mechanic.query.get(mid)
        if mech:
            t.primary_mechanic = mech

    db.session.add(t)
    db.session.commit()
    return ticket_schema.jsonify(t), 201

# LIST (cached)


@ticket_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def list_tickets():
    tickets = ServiceTicket.query.order_by(desc(ServiceTicket.id)).all()
    return jsonify(tickets_schema.dump(tickets)), 200

# READ


@ticket_bp.route("/<int:ticket_id>", methods=["GET"])
@token_required
def get_ticket(ticket_id, *, user_id, role):
    t = ServiceTicket.query.get_or_404(ticket_id)
    return ticket_schema.jsonify(t), 200

# EDIT mechanics (add/remove)


@ticket_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
@token_required
def edit_mechanics(ticket_id, *, user_id, role):
    t = ServiceTicket.query.get_or_404(ticket_id)
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

# ADD part


@ticket_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=["POST"])
@token_required
def add_part(ticket_id, part_id, *, user_id, role):
    t = ServiceTicket.query.get_or_404(ticket_id)
    p = Inventory.query.get_or_404(part_id)
    if p not in t.parts:
        t.parts.append(p)
        db.session.commit()
    return ticket_schema.jsonify(t), 200

# DELETE


@ticket_bp.route("/<int:ticket_id>", methods=["DELETE"])
@limiter.limit("10 per hour")
@token_required
def delete_ticket(ticket_id, *, user_id, role):
    t = ServiceTicket.query.get_or_404(ticket_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"deleted": ticket_id}), 200
