"""
Unit Tests for GST Data Preprocessing & Normalization Engine.
"""

import unittest
import pandas as pd
import numpy as np
from ml.preprocessing import GSTDataPreprocessor

class TestPreprocessing(unittest.TestCase):

    def setUp(self):
        self.preprocessor = GSTDataPreprocessor(scaler_type="robust")
        self.df_entities = pd.DataFrame([
            {"gstin": "27ABCDE1234F1Z5", "state": "Maharashtra", "business_size": "Medium", "category": "Electronics", "is_fraud_flagged": 1},
            {"gstin": "07XYZAB5678G1Z2", "state": "Delhi", "business_size": "Micro", "category": "Scrap", "is_fraud_flagged": 0}
        ])
        self.df_txs = pd.DataFrame([
            {"invoice_id": "INV001", "seller_gstin": "27ABCDE1234F1Z5", "buyer_gstin": "07XYZAB5678G1Z2", "invoice_date": "2026-01-01 10:00:00", "taxable_amount": 1000.0, "cgst": 90.0, "sgst": 90.0, "igst": 0.0, "total_invoice_amount": 1180.0},
            {"invoice_id": "INV001", "seller_gstin": "27ABCDE1234F1Z5", "buyer_gstin": "07XYZAB5678G1Z2", "invoice_date": "2026-01-01 10:00:00", "taxable_amount": 1000.0, "cgst": 90.0, "sgst": 90.0, "igst": 0.0, "total_invoice_amount": 1180.0} # Duplicate
        ])

    def test_clean_transactions(self):
        cleaned = self.preprocessor.clean_transactions(self.df_txs)
        self.assertEqual(len(cleaned), 1)
        self.assertFalse(cleaned.isnull().values.any())

    def test_encode_categoricals(self):
        encoded = self.preprocessor.encode_entity_categoricals(self.df_entities)
        self.assertIn("business_size_code", encoded.columns)
        self.assertIn("state_Maharashtra", encoded.columns)

    def test_scale_features(self):
        df_feat = pd.DataFrame({"gstin": ["A", "B"], "val1": [10.0, 100.0], "val2": [5.0, 50.0]})
        scaled = self.preprocessor.scale_numeric_features(df_feat, ["val1", "val2"])
        self.assertIn("val1_scaled", scaled.columns)
        self.assertTrue(self.preprocessor.is_fitted)

    def test_isolate_ml_matrix(self):
        df_feat = pd.DataFrame({"gstin": ["A", "B"], "val1": [1.0, 2.0], "val2": [3.0, 4.0], "is_fraud_flagged": [0, 1]})
        ids, matrix, names = self.preprocessor.isolate_ml_matrix(df_feat, id_col="gstin")
        self.assertEqual(matrix.shape, (2, 2))
        self.assertIn("val1", names)
        self.assertIn("val2", names)

if __name__ == "__main__":
    unittest.main()
