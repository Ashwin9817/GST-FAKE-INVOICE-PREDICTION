"""
Unit Tests for Graph Schema & Ingestion Query Formats.
"""

import unittest
from graph.schema import (
    CREATE_BUSINESS_CONSTRAINT,
    CREATE_BUSINESS_INDEXES,
    INGEST_BUSINESS_NODES_CYPHER,
    INGEST_TRANSACTION_EDGES_CYPHER
)
from graph.queries import COUNT_NODES_AND_EDGES, DETECT_CIRCULAR_PATHS_CYPHER

class TestGraphSchema(unittest.TestCase):

    def test_cypher_schema_strings(self):
        self.assertIn("CONSTRAINT", CREATE_BUSINESS_CONSTRAINT)
        self.assertIn("b:Business", CREATE_BUSINESS_CONSTRAINT)
        self.assertGreater(len(CREATE_BUSINESS_INDEXES), 0)
        self.assertIn("UNWIND $batch AS row", INGEST_BUSINESS_NODES_CYPHER)
        self.assertIn("UNWIND $batch AS row", INGEST_TRANSACTION_EDGES_CYPHER)

    def test_cypher_queries_formatting(self):
        self.assertIn("MATCH (b:Business)", COUNT_NODES_AND_EDGES)
        self.assertIn("TRANSACTION*3..6", DETECT_CIRCULAR_PATHS_CYPHER)

if __name__ == "__main__":
    unittest.main()
