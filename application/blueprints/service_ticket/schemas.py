from application.extensions import ma
from application.models import ServiceTicket


class TicketSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ServiceTicket
        load_instance = True

    id = ma.auto_field()
    description = ma.auto_field()
    mechanic_id = ma.auto_field()
    user_id = ma.auto_field()
    status = ma.auto_field()
