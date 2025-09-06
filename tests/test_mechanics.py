# tests/test_mechanics.py
from .test_base import APITestCase


class MechanicsRouteTests(APITestCase):
    def test_mechanics_list_public(self):
        res = self.client.get("/mechanics/")
        self.assertEqual(res.status_code, 200)

    def test_mechanic_create_auth_201(self):
        headers = self.auth_headers()
        res = self.client.post(
            "/mechanics/", json={"name": "Casey"}, headers=headers)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()["name"], "Casey")

    def test_mechanic_get_by_id_200(self):
        headers = self.auth_headers()
        mid = self.client.post(
            "/mechanics/", json={"name": "Riley"}, headers=headers).get_json()["id"]
        res = self.client.get(f"/mechanics/{mid}")
        self.assertEqual(res.status_code, 200)

    def test_mechanic_update_put_200(self):
        headers = self.auth_headers()
        mid = self.client.post(
            "/mechanics/", json={"name": "Jess"}, headers=headers).get_json()["id"]
        res = self.client.put(
            f"/mechanics/{mid}", json={"name": "Jess Torque"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["name"], "Jess Torque")

    def test_mechanic_delete_200(self):
        headers = self.auth_headers()
        mid = self.client.post(
            "/mechanics/", json={"name": "Alex"}, headers=headers).get_json()["id"]
        res = self.client.delete(f"/mechanics/{mid}", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["deleted"], mid)

    def test_mechanic_create_400_missing_name(self):
        headers = self.auth_headers()
        res = self.client.post("/mechanics/", json={}, headers=headers)
        self.assertEqual(res.status_code, 400)

    def test_mechanic_get_404(self):
        res = self.client.get("/mechanics/999999")
        self.assertEqual(res.status_code, 404)
