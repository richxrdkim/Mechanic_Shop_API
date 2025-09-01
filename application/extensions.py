from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

# Default/global rate limit (optional-challenge satisfied)
# Storage uses in-memory for dev; swap for Redis in prod (e.g., "redis://localhost:6379/0")
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://",
)

# SimpleCache is fine for dev; use Redis/Memcached in prod
cache = Cache(config={"CACHE_TYPE": "SimpleCache",
              "CACHE_DEFAULT_TIMEOUT": 60})
