"""
Unit Tests for Temporal Feature Engineering Module.
"""

import unittest
import pandas as pd
from ml.feature_engineering import TemporalFeatureExtractor

class TestTemporalFeatures(unittest.TestCase):

    def setUp(self):
        self.extractor = TemporalFeatureExtractor()
        self.df_entities = pd.DataFrame([
            {"gstin": "GSTIN_A"},
            {"gstin": "GSTIN_B"},
            {"gstin": "GSTIN_C"}
        ])
        self.df_txs = pd.DataFrame([
            {"invoice_id": "INV1", "seller_gstin": "GSTIN_A", "buyer_gstin": "GSTIN_B", "invoice_date": "2026-01-01 10:00:00", "total_invoice_amount": 100000.0},
            {"invoice_id": "INV2", "seller_gstin": "GSTIN_A", "buyer_gstin": "GSTIN_B", "invoice_date": "2026-01-01 12:00:00", "total_invoice_amount": 50000.0},
            {"invoice_id": "INV3", "seller_gstin": "GSTIN_B", "buyer_gstin": "GSTIN_C", "invoice_date": "2026-01-02 10:00:00", "total_invoice_amount": 120000.0}
        ])

    def test_extract_temporal_metrics(self):
        df_feats = self.extractor.extract_features(self.df_txs, self.df_entities)
        self.assertEqual(len(df_feats), 3)

        # Inspect GSTIN_A (Seller in 2 transactions)
        row_a = df_feats[df_feats["gstin"] == "GSTIN_A"].iloc[0]
        self.assertEqual(row_a["total_sales"], 150000.0)
        self.assertEqual(row_a["total_purchases"], 0.0)
        self.assertEqual(row_a["sales_count"], 2)
        self.assertEqual(row_a["unique_buyers"], 1)
        self.assertGreater(row_a["burst_24h_max"], 0)
        self.assertEqual(row_a["rapid_repeat_count"], 1) # < 24h between INV1 and INV2

if __name__ == "__main__":
    unittest.main()
