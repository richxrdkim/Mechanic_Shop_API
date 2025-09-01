from application.extensions import ma
from application.models import User
from marshmallow import fields


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    email = ma.auto_field()

# For login payload validation


class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
login_schema = LoginSchema()
