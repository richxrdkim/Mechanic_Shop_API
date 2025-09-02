
from marshmallow import fields, Schema
from application.extensions import ma
from application.models import User, Mechanic, ServiceTicket, Inventory

# --- User ---


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    email = ma.auto_field()


user_schema = UserSchema()
users_schema = UserSchema(many=True)

# For login payload validation


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


login_schema = LoginSchema()

# --- Mechanic ---


class MechanicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Mechanic
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    specialty = ma.auto_field()


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

# "Leaderboard" row (id, name, specialty, tickets_count)


class MechanicWithCountSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    specialty = fields.Str(allow_none=True)
    tickets_count = fields.Int()


mechanics_with_count_schema = MechanicWithCountSchema(many=True)

# --- Inventory ---


class InventorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Inventory
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    price = ma.auto_field()


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

# --- ServiceTicket ---


class ServiceTicketSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ServiceTicket
        load_instance = True

    id = ma.auto_field()
    description = ma.auto_field()
    status = ma.auto_field()
    user = ma.Nested('UserSchema', only=(
        "id", "name", "email"), dump_only=True)
    primary_mechanic = ma.Nested('MechanicSchema', only=(
        "id", "name", "specialty"), dump_only=True)
    mechanics = ma.Nested('MechanicSchema', many=True, only=(
        "id", "name", "specialty"), dump_only=True)
    parts = ma.Nested('InventorySchema', many=True, only=(
        "id", "name", "price"), dump_only=True)


ticket_schema = ServiceTicketSchema()
tickets_schema = ServiceTicketSchema(many=True)
