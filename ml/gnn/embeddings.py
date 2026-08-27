"""
GraphSAGE Node Embedding Extraction Engine.
Executes multi-hop message passing and exports 64-dimensional learned graph node embeddings.
"""

import os
import pandas as pd
import numpy as np
import torch

from ml.gnn.model import GraphSAGENet
from ml.gnn.dataset import GSTGraphDatasetBuilder

class GraphEmbeddingGenerator:
    """Generates and exports 64-dimensional GraphSAGE node embeddings."""

    def __init__(self, embedding_dim: int = 64, seed: int = 42):
        self.embedding_dim = embedding_dim
        torch.manual_seed(seed)
        np.random.seed(seed)

    def generate_embeddings(
        self,
        df_entity_features: pd.DataFrame,
        df_transactions: pd.DataFrame,
        epochs: int = 30,
        output_path: str = None
    ) -> pd.DataFrame:
        """
        Executes GraphSAGE forward message passing pass.
        Returns DataFrame containing gstin and 64-dim embeddings: [gstin, emb_0, ..., emb_63].
        """
        dataset_builder = GSTGraphDatasetBuilder()
        graph_data = dataset_builder.build_graph_tensors(df_entity_features, df_transactions)

        x = graph_data["x"]
        edge_index = graph_data["edge_index"]
        idx_to_gstin = graph_data["idx_to_gstin"]

        in_channels = x.size(1)
        model = GraphSAGENet(in_channels=in_channels, hidden_channels=128, out_channels=self.embedding_dim)

        # Simple self-supervised link reconstruction / feature refinement loss
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

        model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            embeddings = model(x, edge_index)

            # Link reconstruction loss (pull connected edge pairs closer)
            src, dst = edge_index[0], edge_index[1]
            pos_score = (embeddings[src] * embeddings[dst]).sum(dim=-1)
            loss = -torch.log(torch.sigmoid(pos_score) + 1e-15).mean()

            loss.backward()
            optimizer.step()

        # Extract final embeddings
        model.eval()
        with torch.no_grad():
            final_embeddings = model(x, edge_index).numpy()

        emb_cols = [f"emb_{i}" for i in range(self.embedding_dim)]
        emb_data = []

        for idx in range(len(final_embeddings)):
            gstin = idx_to_gstin[idx]
            row_dict = {"gstin": gstin}
            for i, col in enumerate(emb_cols):
                row_dict[col] = float(final_embeddings[idx, i])
            emb_data.append(row_dict)

        df_embeddings = pd.DataFrame(emb_data)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df_embeddings.to_csv(output_path, index=False)

        return df_embeddings
