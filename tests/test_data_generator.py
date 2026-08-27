"""
Unit Tests for Normal GST Transaction & Tax Math Module.
"""

from datetime import datetime
import unittest
from data_generator.normal_transactions import NormalTransactionGenerator

class TestDataGenerator(unittest.TestCase):

    def test_tax_breakdown_intrastate(self):
        gen = NormalTransactionGenerator(seed=42)
        tax_info = gen.calculate_tax_breakdown(
            taxable_amount=100000.0,
            tax_rate=18.0,
            seller_state="Maharashtra",
            buyer_state="Maharashtra"
        )

        self.assertEqual(tax_info["taxable_amount"], 100000.0)
        self.assertEqual(tax_info["total_tax"], 18000.0)
        self.assertEqual(tax_info["cgst"], 9000.0)
        self.assertEqual(tax_info["sgst"], 9000.0)
        self.assertEqual(tax_info["igst"], 0.0)
        self.assertEqual(tax_info["total_invoice_amount"], 118000.0)

    def test_tax_breakdown_interstate(self):
        gen = NormalTransactionGenerator(seed=42)
        tax_info = gen.calculate_tax_breakdown(
            taxable_amount=200000.0,
            tax_rate=12.0,
            seller_state="Maharashtra",
            buyer_state="Delhi"
        )

        self.assertEqual(tax_info["taxable_amount"], 200000.0)
        self.assertEqual(tax_info["total_tax"], 24000.0)
        self.assertEqual(tax_info["cgst"], 0.0)
        self.assertEqual(tax_info["sgst"], 0.0)
        self.assertEqual(tax_info["igst"], 24000.0)
        self.assertEqual(tax_info["total_invoice_amount"], 224000.0)

    def test_generate_single_transaction(self):
        gen = NormalTransactionGenerator(seed=42)
        entities = gen.generate_entities(2)
        seller, buyer = entities[0], entities[1]

        tx = gen.generate_single_transaction(
            invoice_id="INV_TEST_001",
            seller=seller,
            buyer=buyer,
            invoice_date=datetime(2026, 1, 15, 10, 30)
        )

        self.assertEqual(tx["invoice_id"], "INV_TEST_001")
        self.assertEqual(tx["seller_gstin"], seller["gstin"])
        self.assertEqual(tx["buyer_gstin"], buyer["gstin"])
        self.assertEqual(tx["is_fraud"], 0)
        self.assertEqual(tx["fraud_pattern"], "NONE")
        self.assertLess(abs(tx["total_invoice_amount"] - (tx["taxable_amount"] + tx["cgst"] + tx["sgst"] + tx["igst"])), 0.05)

if __name__ == "__main__":
    unittest.main()
