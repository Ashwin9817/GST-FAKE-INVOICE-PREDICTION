"""
Unit Tests for GraphSAGE Neural Network & Dataset Tensors.
"""

import unittest
import torch
import pandas as pd
from ml.gnn.model import GraphSAGENet
from ml.gnn.dataset import GSTGraphDatasetBuilder

class TestGraphSAGE(unittest.TestCase):

    def setUp(self):
        self.df_entities = pd.DataFrame([
            {"gstin": "GSTIN_A", "total_sales": 1000.0, "pagerank": 0.5, "is_fraud_flagged": 0},
            {"gstin": "GSTIN_B", "total_sales": 2000.0, "pagerank": 0.5, "is_fraud_flagged": 1}
        ])
        self.df_txs = pd.DataFrame([
            {"seller_gstin": "GSTIN_A", "buyer_gstin": "GSTIN_B", "total_invoice_amount": 500.0}
        ])
        self.builder = GSTGraphDatasetBuilder()

    def test_build_graph_tensors(self):
        data = self.builder.build_graph_tensors(self.df_entities, self.df_txs)
        self.assertEqual(data["num_nodes"], 2)
        self.assertEqual(data["x"].size(0), 2)
        self.assertEqual(data["edge_index"].size(0), 2)

    def test_gnn_model_forward_pass(self):
        data = self.builder.build_graph_tensors(self.df_entities, self.df_txs)
        x = data["x"]
        edge_index = data["edge_index"]

        model = GraphSAGENet(in_channels=x.size(1), hidden_channels=32, out_channels=64)
        out_embeddings = model(x, edge_index)

        self.assertEqual(out_embeddings.size(0), 2)
        self.assertEqual(out_embeddings.size(1), 64)
        self.assertFalse(torch.isnan(out_embeddings).any())

if __name__ == "__main__":
    unittest.main()
