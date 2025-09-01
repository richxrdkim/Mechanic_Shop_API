from application.extensions import ma
from application.models import ServiceTicket
from application.blueprints.mechanic.schemas import MechanicSchema
from application.blueprints.inventory.schemas import InventorySchema


class TicketSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ServiceTicket
        load_instance = True

    id = ma.auto_field()
    description = ma.auto_field()
    mechanic_id = ma.auto_field()  # legacy FK (ok to keep)
    user_id = ma.auto_field()
    status = ma.auto_field()

    mechanics = ma.Nested(MechanicSchema, many=True, dump_only=True)
    parts = ma.Nested(InventorySchema, many=True, dump_only=True)


ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
