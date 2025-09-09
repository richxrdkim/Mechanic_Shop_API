# tests/test_base.py
from application import create_app  # adjust if your factory lives elsewhere
import os
import unittest

# Make sure env is set BEFORE creating the app
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("TESTING", "1")
# Force SQLite for CI/local tests (fast, no external services)
# Use a file DB so multiple connections share the same schema
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///test_ci.db")

# Prefer importing db from your extensions module if that's your project pattern
try:
    from application.extensions import db
except ImportError:
    # fallback in case you re-export db from application/__init__.py
    from application import db


class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One app + schema per test class (faster, less flaky)
        cls.app = create_app("testing")
        cls.ctx = cls.app.app_context()
        cls.ctx.push()

        # Fresh schema for the suite (or per class)
        db.create_all()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.ctx.pop()

    def auth_headers(self, email="tester@example.com", password="pw"):
        # Sign up
        self.client.post("/users/signup", json={
            "name": "Tester",
            "email": email,
            "password": password
        })
        # Log in to get a token
        res = self.client.post("/users/login", json={
            "email": email,
            "password": password
        })
        self.assertEqual(res.status_code, 200,
                         msg=f"Login failed: {res.get_data(as_text=True)}")
        data = res.get_json() or {}
        token = data.get("token")
        self.assertIsNotNone(token, "No token returned from /users/login")
        return {"Authorization": f"Bearer {token}"}
