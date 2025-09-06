from application.extensions import db
from datetime import datetime

ticket_mechanics = db.Table(
    "ticket_mechanics",
    db.Column("ticket_id", db.Integer, db.ForeignKey(
        "service_ticket.id"), primary_key=True),
    db.Column("mechanic_id", db.Integer, db.ForeignKey(
        "mechanic.id"), primary_key=True),
)

ticket_parts = db.Table(
    "ticket_parts",
    db.Column("ticket_id", db.Integer, db.ForeignKey(
        "service_ticket.id"), primary_key=True),
    db.Column("inventory_id", db.Integer, db.ForeignKey(
        "inventory.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)      # <-- add this
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)


class ServiceTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default="open")

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    primary_mechanic_id = db.Column(
        db.Integer, db.ForeignKey("mechanic.id"), nullable=True)

    primary_mechanic = db.relationship(
        "Mechanic", backref="primary_for", foreign_keys=[primary_mechanic_id])
    mechanics = db.relationship(
        "Mechanic", secondary=ticket_mechanics, backref="tickets", lazy="joined")
    parts = db.relationship(
        "Inventory", secondary=ticket_parts, backref="tickets", lazy="joined")
