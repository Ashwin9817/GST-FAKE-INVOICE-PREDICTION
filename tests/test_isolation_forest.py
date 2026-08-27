"""
Unit Tests for Isolation Forest Anomaly Detection & Risk Normalization.
"""

import unittest
import pandas as pd
import numpy as np
from ml.anomaly.isolation_forest import GSTIsolationForestDetector

class TestIsolationForest(unittest.TestCase):

    def setUp(self):
        self.detector = GSTIsolationForestDetector(n_estimators=50, contamination=0.2, random_state=42)
        # Create normal entities and one extreme outlier
        self.df_fused = pd.DataFrame([
            {"gstin": "NORM_1", "f1": 10.0, "f2": 5.0, "is_fraud_flagged": 0},
            {"gstin": "NORM_2", "f1": 12.0, "f2": 6.0, "is_fraud_flagged": 0},
            {"gstin": "NORM_3", "f1": 11.0, "f2": 5.5, "is_fraud_flagged": 0},
            {"gstin": "ANOMALY_1", "f1": 1000.0, "f2": 500.0, "is_fraud_flagged": 1}
        ])

    def test_train_predict_risk_scoring(self):
        results = self.detector.train_predict(self.df_fused)
        self.assertEqual(len(results), 4)

        self.assertIn("risk_score", results.columns)
        self.assertIn("risk_category", results.columns)
        self.assertIn("anomaly_rank", results.columns)

        # Risk score bounds check (0 - 100)
        self.assertTrue((results["risk_score"] >= 0.0).all())
        self.assertTrue((results["risk_score"] <= 100.0).all())

        # Verify outlier ANOMALY_1 receives highest risk score
        top_anom = results.iloc[0]
        self.assertEqual(top_anom["gstin"], "ANOMALY_1")
        self.assertEqual(top_anom["risk_category"], "HIGH")

if __name__ == "__main__":
    unittest.main()
