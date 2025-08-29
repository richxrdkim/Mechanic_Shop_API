from flask import Flask
from .extensions import db, ma, migrate, limiter
from .blueprints.user.routes import user_bp
from .blueprints.mechanic.routes import mechanic_bp
from .blueprints.service_ticket.routes import ticket_bp
from .extensions import ma, limiter, cache


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # init extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)

    # register blueprints
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanics")
    app.register_blueprint(ticket_bp, url_prefix="/tickets")

    # DIAGNOSTIC: print URL map on boot (remove later)
    with app.app_context():
        print("\n=== URL MAP ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.rule:30} -> {sorted(rule.methods)}")
        print("===============\n")

    # test route defined INSIDE create_app
    @app.route("/ping")
    def ping():
        return "pong", 200

    return app
