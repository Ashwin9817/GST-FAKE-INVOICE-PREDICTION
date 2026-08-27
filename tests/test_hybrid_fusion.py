"""
Unit Tests for Hybrid Feature Fusion Engine.
"""

import unittest
import pandas as pd
from ml.fusion.hybrid_fusion import HybridFeatureFusionEngine

class TestHybridFusion(unittest.TestCase):

    def setUp(self):
        self.fusion = HybridFeatureFusionEngine()
        self.df_feats = pd.DataFrame([
            {"gstin": "GSTIN_A", "sales": 100.0, "pagerank": 0.1},
            {"gstin": "GSTIN_B", "sales": 200.0, "pagerank": 0.2}
        ])
        self.df_embs = pd.DataFrame([
            {"gstin": "GSTIN_A", "emb_0": 0.5, "emb_1": -0.5},
            {"gstin": "GSTIN_B", "emb_0": 0.8, "emb_1": -0.2}
        ])

    def test_fusion_alignment_and_columns(self):
        fused = self.fusion.fuse(self.df_feats, self.df_embs)
        self.assertEqual(len(fused), 2)
        self.assertIn("sales", fused.columns)
        self.assertIn("pagerank", fused.columns)
        self.assertIn("emb_0", fused.columns)
        self.assertIn("emb_1", fused.columns)
        self.assertFalse(fused.isnull().values.any())

if __name__ == "__main__":
    unittest.main()
