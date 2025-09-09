from tests.test_base import DBTestCase
from application.extensions import db
from application.models import User
from werkzeug.security import generate_password_hash


class UsersTestCase(DbTestCase):
    def test_signup_positive(self):
        resp = self.client.post("/users/", json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "password123"
        })
        self.assertEqual(resp.status_code, 201)

    def test_signup_negative_conflict(self):
        # pre-create user
        u = User(name="Alice",
                 email="alice@example.com",
                 password_hash=generate_password_hash("password123"))
        db.session.add(u)
        db.session.commit()

        resp = self.client.post("/users/", json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "password123"
        })
        self.assertEqual(resp.status_code, 409)

    def test_list_users_requires_auth(self):
        resp = self.client.get("/users/")
        self.assertEqual(resp.status_code, 401)

    def test_list_users_positive(self):
        # signup
        self.client.post("/users/", json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "password123"
        })
        # login to get token
        login = self.client.post("/users/login", json={
            "email": "alice@example.com",
            "password": "password123"
        })
        token = login.get_json()["token"]

        # call with auth
        resp = self.client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(resp.status_code, 200)
