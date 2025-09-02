from flask import request, jsonify
from sqlalchemy import func, asc
from application.extensions import db, limiter, cache
from application.models import Mechanic, ServiceTicket, ticket_mechanics
from application.schemas import mechanic_schema, mechanics_schema, mechanics_with_count_schema
from application.util import token_required
from . import mechanic_bp

# CREATE


@mechanic_bp.route("/", methods=["POST"])
@limiter.limit("5 per hour")
@token_required
def create_mechanic(*, user_id, role):
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400
    mech = Mechanic(name=name, specialty=data.get("specialty"))
    db.session.add(mech)
    db.session.commit()
    return mechanic_schema.jsonify(mech), 201

# LIST (cached)


@mechanic_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def list_mechanics():
    mechs = Mechanic.query.order_by(asc(Mechanic.name)).all()
    return jsonify(mechanics_schema.dump(mechs)), 200

# READ


@mechanic_bp.route("/<int:mid>", methods=["GET"])
def get_mechanic(mid):
    mech = Mechanic.query.get_or_404(mid)
    return mechanic_schema.jsonify(mech), 200

# UPDATE


@mechanic_bp.route("/<int:mid>", methods=["PUT"])
@token_required
def update_mechanic(mid, *, user_id, role):
    mech = Mechanic.query.get_or_404(mid)
    data = request.get_json() or {}
    if "name" in data:
        mech.name = data["name"]
    if "specialty" in data:
        mech.specialty = data["specialty"]
    db.session.commit()
    return mechanic_schema.jsonify(mech), 200

# DELETE


@mechanic_bp.route("/<int:mid>", methods=["DELETE"])
@limiter.limit("10 per hour")
@token_required
def delete_mechanic(mid, *, user_id, role):
    mech = Mechanic.query.get_or_404(mid)
    db.session.delete(mech)
    db.session.commit()
    return jsonify({"deleted": mid}), 200

# LEADERBOARD: total tickets per mechanic (primary + M2M)


@mechanic_bp.route("/leaderboard", methods=["GET"])
@cache.cached(timeout=60)
def leaderboard():
    # Primary-mechanic counts
    primary_counts = (
        db.session.query(ServiceTicket.primary_mechanic_id.label("mechanic_id"),
                         func.count(ServiceTicket.id).label("cnt"))
        .group_by(ServiceTicket.primary_mechanic_id)
        .subquery()
    )
    # M2M counts
    m2m_counts = (
        db.session.query(ticket_mechanics.c.mechanic_id.label("mechanic_id"),
                         func.count(ticket_mechanics.c.service_ticket_id).label("cnt"))
        .group_by(ticket_mechanics.c.mechanic_id)
        .subquery()
    )

    q = (
        db.session.query(
            Mechanic.id,
            Mechanic.name,
            Mechanic.specialty,
            (func.coalesce(primary_counts.c.cnt, 0) +
             func.coalesce(m2m_counts.c.cnt, 0)).label("tickets_count"),
        )
        .outerjoin(primary_counts, Mechanic.id == primary_counts.c.mechanic_id)
        .outerjoin(m2m_counts, Mechanic.id == m2m_counts.c.mechanic_id)
        .order_by(func.coalesce(primary_counts.c.cnt, 0) + func.coalesce(m2m_counts.c.cnt, 0).desc())
    )

    rows = q.all()
    return jsonify(mechanics_with_count_schema.dump(rows)), 200
