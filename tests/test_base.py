# tests/test_base.py
from application import create_app
import os
import unittest

# Make sure env is set BEFORE creating the app
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("TESTING", "1")
# In CI, in-memory is fastest; locally you can switch to sqlite:///test_ci.db
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")

try:
    # Prefer your project's shared extensions
    from application.extensions import db
except Exception:
    # Fallback if db is re-exported elsewhere
    from application import db


class DBTestCase(unittest.TestCase):
    """
    Fresh tables for EVERY test method (strong isolation).
    All route tests can inherit from this.
    """
    @classmethod
    def setUpClass(cls):
        # or create_app() if your factory auto-detects TESTING=1
        cls.app = create_app("testing")
        cls.app.testing = True

    def setUp(self):
        # New app context + brand new schema per test
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # Helper to create a token for protected routes
    def auth_headers(self, email="tester@example.com", password="pw"):
        # ✅ Your signup route is POST /users/
        res_signup = self.client.post("/users/", json={
            "name": "Tester",
            "email": email,
            "password": password
        })
        # If user already exists in a test, that's fine; we only need login to succeed.

        # ✅ Your login route is POST /users/login
        res_login = self.client.post("/users/login", json={
            "email": email,
            "password": password
        })
        self.assertEqual(
            res_login.status_code, 200,
            msg=f"Login failed: {res_login.get_data(as_text=True)}"
        )
        token = (res_login.get_json() or {}).get("token")
        self.assertIsNotNone(token, "No token returned from /users/login")
        return {"Authorization": f"Bearer {token}"}
