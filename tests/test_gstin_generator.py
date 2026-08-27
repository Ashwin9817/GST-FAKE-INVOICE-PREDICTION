"""
Unit Tests for GSTIN Generator Module.
"""

import re
import unittest
from data_generator.gstin_generator import GSTINGenerator
from data_generator.config import STATE_CODES

# GSTIN standard regex pattern
GSTIN_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

class TestGSTINGenerator(unittest.TestCase):

    def test_single_gstin_format(self):
        gen = GSTINGenerator(seed=42)
        gstin, state_name = gen.generate_gstin()

        self.assertEqual(len(gstin), 15)
        self.assertIsNotNone(re.match(GSTIN_REGEX, gstin))
        self.assertIn(gstin[:2], STATE_CODES)
        self.assertEqual(STATE_CODES[gstin[:2]], state_name)

    def test_batch_gstin_uniqueness(self):
        gen = GSTINGenerator(seed=42)
        entities = gen.generate_batch(100)

        self.assertEqual(len(entities), 100)
        gstins = [e["gstin"] for e in entities]
        self.assertEqual(len(set(gstins)), 100)

        for e in entities:
            self.assertIsNotNone(re.match(GSTIN_REGEX, e["gstin"]))
            self.assertIn(e["state_code"], STATE_CODES)

if __name__ == "__main__":
    unittest.main()
