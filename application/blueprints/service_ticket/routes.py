from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from application.extensions import db, limiter, cache
from application.models import ServiceTicket, Mechanic, Inventory
from application.utils.util import token_required
from . import ticket_bp
from .schemas import ticket_schema, tickets_schema

# CREATE ticket


@ticket_bp.route("/", methods=["POST"])
@limiter.limit("10 per hour")
@token_required
def create_ticket(*, user_id, role):
    data = request.get_json() or {}
    if "description" not in data:
        return jsonify({"error": "description is required"}), 400
    t = ServiceTicket(
        description=data["description"], user_id=data.get("user_id", user_id))
    # Optional: attach a legacy single mechanic_id
    if "mechanic_id" in data:
        t.mechanic_id = data["mechanic_id"]
    db.session.add(t)
    db.session.commit()
    return ticket_schema.jsonify(t), 201

# GET one


@ticket_bp.route("/<int:ticket_id>", methods=["GET"])
@token_required
def get_ticket(ticket_id, *, user_id, role):
    t = ServiceTicket.query.get_or_404(ticket_id)
    return ticket_schema.jsonify(t), 200

# LIST tickets (cached)


@ticket_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def list_tickets():
    ts = ServiceTicket.query.order_by(ServiceTicket.id.desc()).all()
    return jsonify(tickets_schema.dump(ts)), 200

# UPDATE mechanics on a ticket (advanced query)


@ticket_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
@token_required
def edit_ticket_mechanics(ticket_id, *, user_id, role):
    """
    Body: {"add_ids":[...], "remove_ids":[...]}
    """
    t = ServiceTicket.query.get_or_404(ticket_id)
    data = request.get_json() or {}
    add_ids = data.get("add_ids", []) or []
    remove_ids = data.get("remove_ids", []) or []

    if not isinstance(add_ids, list) or not isinstance(remove_ids, list):
        raise BadRequest("add_ids and remove_ids must be lists")

    if add_ids:
        to_add = Mechanic.query.filter(Mechanic.id.in_(add_ids)).all()
        found = {m.id for m in to_add}
        missing = sorted(set(add_ids) - found)
        if missing:
            raise BadRequest(f"Unknown mechanic IDs: {missing}")
        for m in to_add:
            if m not in t.mechanics:
                t.mechanics.append(m)

    if remove_ids:
        to_remove = Mechanic.query.filter(Mechanic.id.in_(remove_ids)).all()
        for m in to_remove:
            if m in t.mechanics:
                t.mechanics.remove(m)

    db.session.commit()
    return ticket_schema.jsonify(t), 200

# ADD a single inventory part to a ticket


@ticket_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=["POST"])
@token_required
def add_part_to_ticket(ticket_id, part_id, *, user_id, role):
    t = ServiceTicket.query.get_or_404(ticket_id)
    part = Inventory.query.get_or_404(part_id)
    if part not in t.parts:
        t.parts.append(part)
        db.session.commit()
    return ticket_schema.jsonify(t), 200

# DELETE ticket


@ticket_bp.route("/<int:ticket_id>", methods=["DELETE"])
@limiter.limit("10 per hour")
@token_required
def delete_ticket(ticket_id, *, user_id, role):
    t = ServiceTicket.query.get_or_404(ticket_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": f"Ticket {ticket_id} deleted"}), 200
