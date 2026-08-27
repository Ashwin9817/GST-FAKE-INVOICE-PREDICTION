"""
Unit Tests for FastAPI Backend REST API Services.
"""

import unittest
from fastapi.testclient import TestClient
from backend.app.main import app

class TestBackendAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["status"], "ONLINE")

    def test_stats_endpoint(self):
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("total_entities", json_data)
        self.assertIn("total_transactions", json_data)

    def test_msme_risk_check_endpoint(self):
        payload = {"supplier_gstin": "27ABCDE1234F1Z5"}
        response = self.client.post("/api/risk-check", json=payload)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["supplier_gstin"], "27ABCDE1234F1Z5")

if __name__ == "__main__":
    unittest.main()
