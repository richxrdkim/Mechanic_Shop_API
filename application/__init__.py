from flask import Flask
from .extensions import db, ma, migrate, limiter, cache
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)

    # Imports AFTER extensions are ready
    from .blueprints.user import user_bp
    from .blueprints.mechanic import mechanic_bp
    from .blueprints.service_ticket import ticket_bp
    from .blueprints.inventory import inventory_bp

    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanics")
    app.register_blueprint(ticket_bp, url_prefix="/tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    return app
