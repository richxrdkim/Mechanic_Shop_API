
from application.extensions import db

# --- Association tables ---
ticket_mechanics = db.Table(
    "ticket_mechanics",
    db.Column("service_ticket_id", db.Integer, db.ForeignKey(
        "service_tickets.id"), primary_key=True),
    db.Column("mechanic_id", db.Integer, db.ForeignKey(
        "mechanics.id"), primary_key=True),
    db.UniqueConstraint("service_ticket_id", "mechanic_id",
                        name="uq_ticket_mechanic"),
)

inventory_tickets = db.Table(
    "inventory_tickets",
    db.Column("service_ticket_id", db.Integer, db.ForeignKey(
        "service_tickets.id"), primary_key=True),
    db.Column("inventory_id", db.Integer, db.ForeignKey(
        "inventory.id"), primary_key=True),
    db.UniqueConstraint("service_ticket_id", "inventory_id",
                        name="uq_ticket_part"),
)

# --- Models ---


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    tickets = db.relationship(
        "ServiceTicket", back_populates="user", lazy="select")


class Mechanic(db.Model):
    __tablename__ = "mechanics"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(120))

    tickets_primary = db.relationship(
        "ServiceTicket", back_populates="primary_mechanic", lazy="select")
    tickets = db.relationship(
        "ServiceTicket",
        secondary=ticket_mechanics,
        back_populates="mechanics",
        lazy="select",
    )


class Inventory(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    tickets = db.relationship(
        "ServiceTicket",
        secondary=inventory_tickets,
        back_populates="parts",
        lazy="select",
    )


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default="open", nullable=False)

    # Optional single "primary" mechanic
    primary_mechanic_id = db.Column(db.Integer, db.ForeignKey("mechanics.id"))
    primary_mechanic = db.relationship(
        "Mechanic", back_populates="tickets_primary", foreign_keys=[primary_mechanic_id])

    # The requesting user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="tickets")

    # M2M helpers
    mechanics = db.relationship(
        "Mechanic",
        secondary=ticket_mechanics,
        back_populates="tickets",
        lazy="select",
    )
    parts = db.relationship(
        "Inventory",
        secondary=inventory_tickets,
        back_populates="tickets",
        lazy="select",
    )
