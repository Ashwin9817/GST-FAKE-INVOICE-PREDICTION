"""
Unit Tests for Explainable Alert Generator.
"""

import unittest
from explainability.alert_generator import ExplainableAlertGenerator

class TestExplainability(unittest.TestCase):

    def setUp(self):
        self.generator = ExplainableAlertGenerator()

    def test_alert_generation_circular_loop(self):
        risk_profile = {"final_risk_score": 85.0, "risk_category": "HIGH"}
        feat_profile = {"has_loop": 1, "shortest_loop_dist": 3, "burst_24h_max": 20}

        explanation = self.generator.generate_explanation("27ABCDE1234F1Z5", risk_profile, feat_profile)
        self.assertEqual(explanation["risk_category"], "HIGH")
        self.assertGreater(len(explanation["reasons"]), 0)

        codes = [r["code"] for r in explanation["reasons"]]
        self.assertIn("CIRCULAR_PATH", codes)
        self.assertIn("HIGH_VELOCITY", codes)
        self.assertIn("3-hop", explanation["natural_language_summary"])

if __name__ == "__main__":
    unittest.main()
