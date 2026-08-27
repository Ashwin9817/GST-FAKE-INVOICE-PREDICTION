"""
Unit Tests for Fraud Injection Engine.
"""

from datetime import datetime
import unittest
from data_generator.normal_transactions import NormalTransactionGenerator
from data_generator.fraud_injection import FraudInjectionEngine
from data_generator.config import FRAUD_TYPES

class TestFraudInjection(unittest.TestCase):

    def test_circular_trading_injection(self):
        norm_gen = NormalTransactionGenerator(seed=42)
        fraud_engine = FraudInjectionEngine(seed=42)
        entities = norm_gen.generate_entities(10)

        txs, flagged, _ = fraud_engine.inject_circular_trading(
            entities=entities,
            start_invoice_id=1,
            start_date=datetime(2026, 1, 1),
            cycle_length=3,
            num_cycles=2,
            normal_gen_ref=norm_gen
        )

        self.assertEqual(len(txs), 6)  # 2 cycles * 3 hops = 6 transactions
        self.assertGreater(len(flagged), 0)
        for tx in txs:
            self.assertEqual(tx["is_fraud"], 1)
            self.assertEqual(tx["fraud_pattern"], FRAUD_TYPES["CIRCULAR_TRADING"])
            self.assertIn("GROUP_CIRC", tx["fraud_group_id"])

    def test_split_invoicing_sub_threshold(self):
        norm_gen = NormalTransactionGenerator(seed=42)
        fraud_engine = FraudInjectionEngine(seed=42)
        entities = norm_gen.generate_entities(10)

        txs, flagged, _ = fraud_engine.inject_split_invoicing(
            entities=entities,
            start_invoice_id=1,
            start_date=datetime(2026, 1, 1),
            num_split_groups=1,
            splits_per_group=5,
            normal_gen_ref=norm_gen
        )

        self.assertEqual(len(txs), 5)
        for tx in txs:
            self.assertEqual(tx["is_fraud"], 1)
            self.assertEqual(tx["fraud_pattern"], FRAUD_TYPES["SPLIT_INVOICING"])
            # Sub-threshold e-way bill amount check (less than ₹50,000)
            self.assertLess(tx["taxable_amount"], 50000.0)

if __name__ == "__main__":
    unittest.main()
