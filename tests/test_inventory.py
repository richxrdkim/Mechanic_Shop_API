# tests/test_inventory.py
from .test_base import APITestCase


class InventoryRouteTests(APITestCase):
    def test_inventory_list_public(self):
        res = self.client.get("/inventory/")
        self.assertEqual(res.status_code, 200)

    def test_inventory_create_auth_201(self):
        headers = self.auth_headers()
        res = self.client.post(
            "/inventory/", json={"name": "Oil Filter"}, headers=headers)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()["name"], "Oil Filter")

    def test_inventory_get_by_id_200(self):
        headers = self.auth_headers()
        pid = self.client.post(
            "/inventory/", json={"name": "Belt"}, headers=headers).get_json()["id"]
        res = self.client.get(f"/inventory/{pid}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["id"], pid)

    def test_inventory_update_put_200(self):
        headers = self.auth_headers()
        pid = self.client.post(
            "/inventory/", json={"name": "Rotor"}, headers=headers).get_json()["id"]
        res = self.client.put(
            f"/inventory/{pid}", json={"name": "Rotor XL"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["name"], "Rotor XL")

    def test_inventory_delete_200(self):
        headers = self.auth_headers()
        pid = self.client.post(
            "/inventory/", json={"name": "Pad"}, headers=headers).get_json()["id"]
        res = self.client.delete(f"/inventory/{pid}", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["deleted"], pid)

    def test_inventory_create_400_missing_name(self):
        headers = self.auth_headers()
        res = self.client.post("/inventory/", json={}, headers=headers)
        self.assertEqual(res.status_code, 400)

    def test_inventory_get_404(self):
        res = self.client.get("/inventory/999999")
        self.assertEqual(res.status_code, 404)
