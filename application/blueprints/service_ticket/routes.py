from flask import Blueprint, request, jsonify
from application.models import ServiceTicket, User, Mechanic
from application.extensions import db, limiter, cache
from .schemas import TicketSchema
from application.utils.util import token_required  # <-- add this

ticket_bp = Blueprint("ticket_bp", __name__)

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

# CREATE (Protected)


@ticket_bp.route("/", methods=["POST"])
@token_required
def create_ticket(*, user_id):
    data = request.get_json() or {}

    # Optional sanity checks (as you had)
    if "user_id" in data and data["user_id"]:
        User.query.get_or_404(data["user_id"])
    if "mechanic_id" in data and data["mechanic_id"]:
        Mechanic.query.get_or_404(data["mechanic_id"])

    ticket = ticket_schema.load(data)
    db.session.add(ticket)
    db.session.commit()
    return ticket_schema.jsonify(ticket), 201

# READ all (Protected + Cached after auth)


@ticket_bp.route("/", methods=["GET"])
@token_required
@cache.cached(timeout=60)
def list_tickets(*, user_id):
    tickets = ServiceTicket.query.all()
    return jsonify(tickets_schema.dump(tickets)), 200

# READ one (Protected)


@ticket_bp.route("/<int:ticket_id>", methods=["GET"])
@token_required
def get_ticket(ticket_id, *, user_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    return ticket_schema.jsonify(ticket), 200

# UPDATE (Protected)


@ticket_bp.route("/<int:ticket_id>", methods=["PUT"])
@token_required
def update_ticket(ticket_id, *, user_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    data = request.get_json() or {}
    for k, v in data.items():
        if hasattr(ticket, k):
            setattr(ticket, k, v)
    db.session.commit()
    return ticket_schema.jsonify(ticket), 200

# DELETE (Protected)


@ticket_bp.route("/<int:ticket_id>", methods=["DELETE"])
@token_required
def delete_ticket(ticket_id, *, user_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Ticket {ticket_id} deleted"}), 200
