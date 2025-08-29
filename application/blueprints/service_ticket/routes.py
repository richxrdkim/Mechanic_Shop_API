from flask import Blueprint, request, jsonify
from application.models import ServiceTicket, User, Mechanic
from application.extensions import db
from .schemas import TicketSchema

ticket_bp = Blueprint("ticket_bp", __name__)

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

# CREATE


@ticket_bp.route("/", methods=["POST"])
def create_ticket():
    data = request.get_json() or {}
    # (Optional) quick sanity checks
    if "user_id" in data and data["user_id"]:
        User.query.get_or_404(data["user_id"])
    if "mechanic_id" in data and data["mechanic_id"]:
        Mechanic.query.get_or_404(data["mechanic_id"])

    ticket = ticket_schema.load(data)
    db.session.add(ticket)
    db.session.commit()
    return ticket_schema.jsonify(ticket), 201

# READ all


@ticket_bp.route("/", methods=["GET"])
def list_tickets():
    tickets = ServiceTicket.query.all()
    return jsonify(tickets_schema.dump(tickets)), 200

# READ one


@ticket_bp.route("/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    return ticket_schema.jsonify(ticket), 200

# UPDATE


@ticket_bp.route("/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    data = request.get_json() or {}
    for k, v in data.items():
        if hasattr(ticket, k):
            setattr(ticket, k, v)
    db.session.commit()
    return ticket_schema.jsonify(ticket), 200

# DELETE


@ticket_bp.route("/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Ticket {ticket_id} deleted"}), 200
