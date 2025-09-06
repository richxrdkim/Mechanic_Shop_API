import unittest
from application import create_app, db


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

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
        # Helpful assertions if something breaks
        self.assertEqual(res.status_code, 200,
                         msg=f"Login failed: {res.get_data(as_text=True)}")
        data = res.get_json() or {}
        token = data.get("token")
        self.assertIsNotNone(token, "No token returned from /users/login")
        return {"Authorization": f"Bearer {token}"}
