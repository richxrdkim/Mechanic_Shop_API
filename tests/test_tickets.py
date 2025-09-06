# tests/test_tickets.py
from .test_base import APITestCase


class TicketsRouteTests(APITestCase):
    def test_ticket_create_auth_201(self):
        headers = self.auth_headers()
        res = self.client.post(
            "/tickets/", json={"description": "Check brakes"}, headers=headers)
        self.assertEqual(res.status_code, 201)
        self.assertIn("description", res.get_json())

    def test_ticket_list_auth_200(self):
        headers = self.auth_headers()
        self.client.post(
            "/tickets/", json={"description": "Noise"}, headers=headers)
        res = self.client.get("/tickets/", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.get_json(), list)

    def test_ticket_get_by_id_200(self):
        headers = self.auth_headers()
        tid = self.client.post(
            "/tickets/", json={"description": "Vibration"}, headers=headers).get_json()["id"]
        res = self.client.get(f"/tickets/{tid}", headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_ticket_edit_mechanics_put_200(self):
        headers = self.auth_headers()
        # need a mechanic to add
        mid = self.client.post(
            "/mechanics/", json={"name": "Pat"}, headers=headers).get_json()["id"]
        tid = self.client.post(
            "/tickets/", json={"description": "Alignment"}, headers=headers).get_json()["id"]
        res = self.client.put(
            f"/tickets/{tid}/edit", json={"add_ids": [mid]}, headers=headers)
        self.assertEqual(res.status_code, 200)
        # optional: assert mechanic id present in response

    def test_ticket_add_part_post_200(self):
        headers = self.auth_headers()
        pid = self.client.post(
            "/inventory/", json={"name": "Oil Filter"}, headers=headers).get_json()["id"]
        tid = self.client.post(
            "/tickets/", json={"description": "Oil change"}, headers=headers).get_json()["id"]
        res = self.client.post(
            f"/tickets/{tid}/add-part/{pid}", headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_ticket_delete_200(self):
        headers = self.auth_headers()
        tid = self.client.post(
            "/tickets/", json={"description": "Squeal"}, headers=headers).get_json()["id"]
        res = self.client.delete(f"/tickets/{tid}", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["deleted"], tid)

    def test_ticket_create_400_missing_description(self):
        headers = self.auth_headers()
        res = self.client.post("/tickets/", json={}, headers=headers)
        self.assertEqual(res.status_code, 400)

    def test_ticket_get_404(self):
        headers = self.auth_headers()
        res = self.client.get("/tickets/999999", headers=headers)
        self.assertEqual(res.status_code, 404)
