import os
from flask import Flask
from flasgger import Swagger

from config import DevelopmentConfig, TestingConfig, ProductionConfig
from application.extensions import db, ma, migrate, limiter, cache


def _swagger_template():
    return {
        "swagger": "2.0",
        "info": {"title": "Mechanic Shop API", "version": "1.0.0"},
        "basePath": "/",
        "schemes": ["http"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Bearer token. Example: **Bearer eyJ...**",
            }
        },
        "definitions": {
            "LoginPayload": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "example": "alice@example.com"},
                    "password": {"type": "string", "example": "password123"},
                },
                "example": {"email": "alice@example.com", "password": "password123"},
            },
            "AuthResponse": {
                "type": "object",
                "properties": {"token": {"type": "string", "example": "eyJhbGciOiJI..."}}},
            "SignupPayload": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "name": {"type": "string", "example": "Alice"},
                    "email": {"type": "string", "example": "alice@example.com"},
                    "password": {"type": "string", "example": "password123"},
                },
                "example": {"name": "Alice", "email": "alice@example.com", "password": "password123"},
            },
            "MechanicPayload": {
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string", "example": "Sam Wrench"}},
            },
            "InventoryPayload": {
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string", "example": "Oil Filter"}},
            },
            "TicketPayload": {
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {"type": "string", "example": "Oil change + tire rotation"},
                    "primary_mechanic_id": {"type": "integer", "example": 1},
                },
            },
            "UserResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "email": {"type": "string", "example": "alice@example.com"},
                },
            },
            "MechanicResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "name": {"type": "string", "example": "Sam Wrench"},
                },
            },
            "InventoryResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 10},
                    "name": {"type": "string", "example": "Oil Filter"},
                },
            },
            "TicketResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 3},
                    "description": {"type": "string", "example": "Oil change + tire rotation"},
                    "status": {"type": "string", "example": "open"},
                    "primary_mechanic_id": {"type": "integer", "example": 1},
                },
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {"error": {"type": "string", "example": "Unauthorized"}},
            },
        },
    }


def _select_config_name(explicit: str | None) -> str:
    """
    Decide which config to use.
    Priority:
      1) Explicit arg if provided (e.g., 'testing')
      2) TESTING=1  -> 'testing'
      3) FLASK_ENV  -> 'production' | 'testing' | 'development' (default: development)
    """
    if explicit:
        return explicit
    if os.getenv("TESTING") == "1":
        return "testing"
    return os.getenv("FLASK_ENV", "development").lower()


def _load_config(app: Flask, config_name: str) -> None:
    if config_name == "testing":
        app.config.from_object(TestingConfig)
    elif config_name == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    # Choose and load configuration
    chosen = _select_config_name(config_name)
    _load_config(app, chosen)

    # Init extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    # Respect RATELIMIT_ENABLED=False under testing (from TestingConfig)
    limiter.init_app(app)
    cache.init_app(app)

    # Swagger
    Swagger(app, template=_swagger_template())

    # Blueprints
    from application.blueprints.user import user_bp
    from application.blueprints.service_ticket import ticket_bp
    from application.blueprints.mechanic import mechanic_bp
    from application.blueprints.inventory import inventory_bp

    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(ticket_bp, url_prefix="/tickets")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanics")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    return app
