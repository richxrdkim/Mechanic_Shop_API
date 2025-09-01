from application.extensions import ma
from application.models import Mechanic


class MechanicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Mechanic
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    specialty = ma.auto_field()


class MechanicWithCountSchema(MechanicSchema):
    tickets_count = ma.Integer(dump_only=True)


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanics_with_count_schema = MechanicWithCountSchema(many=True)
