from flask import Blueprint

ticket_bp = Blueprint("ticket_bp", __name__)

from . import routes  # noqa: E402,F401
