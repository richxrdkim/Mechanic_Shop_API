from application.extensions import db

# --- Many-to-many: tickets ↔ mechanics
ticket_mechanics = db.Table(
    "ticket_mechanics",
    db.Column("service_ticket_id", db.Integer, db.ForeignKey(
        "service_tickets.id"), primary_key=True),
    db.Column("mechanic_id", db.Integer, db.ForeignKey(
        "mechanics.id"), primary_key=True),
    db.UniqueConstraint("service_ticket_id", "mechanic_id",
                        name="uq_ticket_mechanic"),
)

# --- Many-to-many: tickets ↔ inventory parts
inventory_tickets = db.Table(
    "inventory_tickets",
    db.Column("service_ticket_id", db.Integer, db.ForeignKey(
        "service_tickets.id"), primary_key=True),
    db.Column("inventory_id", db.Integer, db.ForeignKey(
        "inventory.id"), primary_key=True),
    db.UniqueConstraint("service_ticket_id", "inventory_id",
                        name="uq_ticket_part"),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))  # for login
    tickets = db.relationship("ServiceTicket", backref="user", lazy=True)


class Mechanic(db.Model):
    __tablename__ = "mechanics"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))
    # M2M: tickets worked on
    tickets = db.relationship(
        "ServiceTicket",
        secondary=ticket_mechanics,
        back_populates="mechanics",
        lazy="select",
    )


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    # Optional legacy single-mechanic FK; safe to keep
    mechanic_id = db.Column(db.Integer, db.ForeignKey("mechanics.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(50), default="open")

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
