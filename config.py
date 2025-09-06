import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    # Caching & rate limit defaults (can be overridden)
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60
    RATELIMIT_ENABLED = True


class DevelopmentConfig(Config):
    # Use env if provided, fall back to local SQLite for dev
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    RATELIMIT_ENABLED = False          # <— add this line


class ProductionConfig(Config):
    # Must be set by environment in prod
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
