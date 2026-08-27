"""
Graph Dataset Builder.
Converts CSV entity features and transaction directed edges into PyTorch Graph Tensors.
"""

import pandas as pd
import numpy as np
import torch
from ml.preprocessing import GSTDataPreprocessor

class GSTGraphDatasetBuilder:
    """Builds PyTorch Graph Dataset Tensors (x, edge_index) from processed feature tables."""

    def __init__(self):
        self.preprocessor = GSTDataPreprocessor()

    def build_graph_tensors(self, df_entity_features: pd.DataFrame, df_transactions: pd.DataFrame) -> dict:
        """
        Builds PyTorch graph dataset tensors:
        x: [num_nodes, num_features]
        edge_index: [2, num_edges]
        gstin_to_idx: mapping dictionary
        idx_to_gstin: reverse mapping dictionary
        """
        df_feat = df_entity_features.copy()
        df_tx = df_transactions.copy()

        # Map GSTIN string to integer node ID
        gstins = df_feat["gstin"].unique().tolist()
        gstin_to_idx = {gstin: idx for idx, gstin in enumerate(gstins)}
        idx_to_gstin = {idx: gstin for gstin, idx in gstin_to_idx.items()}

        # Isolate numerical features (excluding raw string IDs & labels)
        ids_df, feature_matrix, feature_names = self.preprocessor.isolate_ml_matrix(df_feat, id_col="gstin")

        x_tensor = torch.tensor(feature_matrix, dtype=torch.float32)

        # Build edge_index [2, E]
        edge_src = []
        edge_dst = []

        for _, row in df_tx.iterrows():
            s_gstin = row["seller_gstin"]
            b_gstin = row["buyer_gstin"]
            if s_gstin in gstin_to_idx and b_gstin in gstin_to_idx:
                edge_src.append(gstin_to_idx[s_gstin])
                edge_dst.append(gstin_to_idx[b_gstin])

        if not edge_src:
            # Self-loop fallback if no valid edges
            edge_src = list(range(len(gstins)))
            edge_dst = list(range(len(gstins)))

        edge_index_tensor = torch.tensor([edge_src, edge_dst], dtype=torch.long)

        return {
            "x": x_tensor,
            "edge_index": edge_index_tensor,
            "gstin_to_idx": gstin_to_idx,
            "idx_to_gstin": idx_to_gstin,
            "feature_names": feature_names,
            "num_nodes": len(gstins),
            "num_edges": edge_index_tensor.size(1)
        }
