from flask import request, jsonify
from sqlalchemy import func, desc
from application.extensions import db, limiter, cache
from application.models import Mechanic, ticket_mechanics
from application.utils.util import token_required, mechanic_token_required
from . import mechanic_bp
from .schemas import mechanic_schema, mechanics_schema, mechanics_with_count_schema

# CREATE mechanic


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

# LIST mechanics (cached)


@mechanic_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def list_mechanics():
    mechs = Mechanic.query.order_by(Mechanic.name.asc()).all()
    return jsonify(mechanics_schema.dump(mechs)), 200

# UPDATE mechanic


@mechanic_bp.route("/<int:mechanic_id>", methods=["PUT"])
@token_required
def update_mechanic(mechanic_id, *, user_id, role):
    mech = Mechanic.query.get_or_404(mechanic_id)
    data = request.get_json() or {}
    mech.name = data.get("name", mech.name)
    mech.specialty = data.get("specialty", mech.specialty)
    db.session.commit()
    return mechanic_schema.jsonify(mech), 200

# DELETE mechanic


@mechanic_bp.route("/<int:mechanic_id>", methods=["DELETE"])
@limiter.limit("5 per hour")
@token_required
def delete_mechanic(mechanic_id, *, user_id, role):
    mech = Mechanic.query.get_or_404(mechanic_id)
    db.session.delete(mech)
    db.session.commit()
    return jsonify({"message": f"Mechanic {mechanic_id} deleted"}), 200

# LEADERBOARD (advanced query, cached)


@mechanic_bp.route("/leaderboard", methods=["GET"])
@token_required
@cache.cached(timeout=60, query_string=True)
def mechanics_leaderboard(*, user_id, role):
    limit = request.args.get("limit", 50)
    try:
        limit = min(int(limit), 200)
        if limit <= 0:
            limit = 50
    except ValueError:
        limit = 50

    q = (
        db.session.query(
            Mechanic,
            func.count(ticket_mechanics.c.service_ticket_id).label(
                "tickets_count"),
        )
        .outerjoin(ticket_mechanics, Mechanic.id == ticket_mechanics.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(desc("tickets_count"), Mechanic.name.asc())
        .limit(limit)
    )
    rows = q.all()
    payload = [
        {"id": m.id, "name": m.name, "specialty": m.specialty,
            "tickets_count": int(c or 0)}
        for m, c in rows
    ]
    return jsonify(mechanics_with_count_schema.dump(payload)), 200
