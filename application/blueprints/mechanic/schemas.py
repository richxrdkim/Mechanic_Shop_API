from application.extensions import ma
from application.models import Mechanic


class MechanicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Mechanic
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    specialty = ma.auto_field()
