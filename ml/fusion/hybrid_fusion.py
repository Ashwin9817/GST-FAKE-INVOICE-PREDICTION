"""
Hybrid Feature Fusion Engine (Proposed Novelty #1).
Performs feature-level fusion combining transactional metrics, topological graph parameters, and learned GraphSAGE node embeddings.
"""

import os
import pandas as pd
import numpy as np

class HybridFeatureFusionEngine:
    """Combines transactional, manual graph, and learned GNN embeddings into a single feature matrix."""

    def fuse(
        self,
        df_entity_features: pd.DataFrame,
        df_gnn_embeddings: pd.DataFrame,
        output_path: str = None
    ) -> pd.DataFrame:
        """
        Fuses transactional features, graph topological features, and GNN embeddings.
        Returns unified DataFrame.
        """
        # Ensure merge alignment on gstin
        fused = pd.merge(df_entity_features, df_gnn_embeddings, on="gstin", how="inner")

        # Fill any missing values with 0.0
        fused = fused.fillna(0.0)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            fused.to_csv(output_path, index=False)

        return fused
