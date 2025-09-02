from flask import Blueprint

user_bp = Blueprint("user_bp", __name__)

# Import routes after the blueprint exists
from . import routes  # noqa: E402,F401
