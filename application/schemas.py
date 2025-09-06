from application.extensions import ma
from application.models import User, Mechanic, Inventory, ServiceTicket


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
    id = ma.auto_field()
    email = ma.auto_field()


class MechanicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Mechanic
        load_instance = True
    id = ma.auto_field()
    name = ma.auto_field()


class InventorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Inventory
        load_instance = True
    id = ma.auto_field()
    name = ma.auto_field()


class TicketSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
    id = ma.auto_field()
    description = ma.auto_field()
    status = ma.auto_field()
    primary_mechanic_id = ma.auto_field()
    mechanics = ma.List(ma.Nested(MechanicSchema))
    parts = ma.List(ma.Nested(InventorySchema))


user_schema = UserSchema()
users_schema = UserSchema(many=True)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
