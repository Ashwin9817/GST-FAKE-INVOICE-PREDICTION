"""
Unit Tests for Risk Score Propagation Engine.
"""

import unittest
import pandas as pd
from ml.propagation.risk_propagation import RiskPropagationEngine

class TestRiskPropagation(unittest.TestCase):

    def setUp(self):
        self.engine = RiskPropagationEngine(decay_factor=0.5, max_hops=2)
        # Entity A is direct high-risk anomaly (score 90)
        self.df_risk = pd.DataFrame([
            {"gstin": "ENTITY_A", "risk_score": 90.0},
            {"gstin": "ENTITY_B", "risk_score": 20.0},
            {"gstin": "ENTITY_C", "risk_score": 10.0}
        ])
        # Chain A -> B -> C
        self.df_txs = pd.DataFrame([
            {"seller_gstin": "ENTITY_A", "buyer_gstin": "ENTITY_B"},
            {"seller_gstin": "ENTITY_B", "buyer_gstin": "ENTITY_C"}
        ])

    def test_propagate_risk_decay(self):
        res = self.engine.propagate_risk(self.df_risk, self.df_txs)
        self.assertEqual(len(res), 3)

        # ENTITY_B (1-hop from A): 90 * 0.5 = 45.0
        row_b = res[res["gstin"] == "ENTITY_B"].iloc[0]
        self.assertEqual(row_b["propagated_network_risk"], 45.0)
        self.assertEqual(row_b["final_risk_score"], 45.0)

        # ENTITY_C (2-hop from A): 90 * 0.25 = 22.5
        row_c = res[res["gstin"] == "ENTITY_C"].iloc[0]
        self.assertEqual(row_c["propagated_network_risk"], 22.5)

if __name__ == "__main__":
    unittest.main()
