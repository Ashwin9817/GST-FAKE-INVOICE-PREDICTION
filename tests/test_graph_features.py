"""
Unit Tests for Graph Topological Feature Extraction Module.
"""

import unittest
import pandas as pd
from graph.graph_features import GraphFeatureExtractor

class TestGraphFeatures(unittest.TestCase):

    def setUp(self):
        self.extractor = GraphFeatureExtractor()
        # Create 3 entities forming a circular cycle (A -> B -> C -> A)
        self.df_entities = pd.DataFrame([
            {"gstin": "NODE_A"},
            {"gstin": "NODE_B"},
            {"gstin": "NODE_C"}
        ])
        self.df_txs = pd.DataFrame([
            {"invoice_id": "INV1", "seller_gstin": "NODE_A", "buyer_gstin": "NODE_B", "total_invoice_amount": 1000.0},
            {"invoice_id": "INV2", "seller_gstin": "NODE_B", "buyer_gstin": "NODE_C", "total_invoice_amount": 1000.0},
            {"invoice_id": "INV3", "seller_gstin": "NODE_C", "buyer_gstin": "NODE_A", "total_invoice_amount": 1000.0}
        ])

    def test_extract_graph_topology(self):
        df_feats = self.extractor.extract_features(self.df_txs, self.df_entities)
        self.assertEqual(len(df_feats), 3)

        # Inspect NODE_A
        row_a = df_feats[df_feats["gstin"] == "NODE_A"].iloc[0]
        self.assertEqual(row_a["in_degree"], 1)
        self.assertEqual(row_a["out_degree"], 1)
        self.assertEqual(row_a["total_degree"], 2)
        self.assertGreater(row_a["pagerank"], 0.0)

        # Verify circular loop detection (Cycle of length 3)
        self.assertEqual(row_a["has_loop"], 1)
        self.assertEqual(row_a["shortest_loop_dist"], 3)
        self.assertGreater(row_a["loop_count"], 0)

if __name__ == "__main__":
    unittest.main()
