"""
Contrastive Representation Refinement Engine (Proposed Novelty #2).
Learns stable discriminative representations under limited label availability via self-supervised contrastive optimization.
"""

import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn

from ml.contrastive.augmentations import ContrastiveAugmentor
from ml.contrastive.loss import InfoNCELoss
from ml.preprocessing import GSTDataPreprocessor

class ContrastiveProjectionEncoder(nn.Module):
    """MLP Projection Encoder for Contrastive Representation Learning."""

    def __init__(self, in_features: int, hidden_dim: int = 128, proj_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, proj_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

class ContrastiveRefinementEngine:
    """Orchestrates contrastive representation refinement training."""

    def __init__(self, proj_dim: int = 64, temperature: float = 0.5, seed: int = 42):
        self.proj_dim = proj_dim
        self.temperature = temperature
        torch.manual_seed(seed)
        np.random.seed(seed)
        self.preprocessor = GSTDataPreprocessor()
        self.augmentor = ContrastiveAugmentor(seed=seed)

    def train_refine(
        self,
        df_entity_features: pd.DataFrame,
        epochs: int = 25,
        output_path: str = None
    ) -> pd.DataFrame:
        """
        Executes self-supervised contrastive refinement.
        Returns DataFrame containing gstin and contrastive refined embeddings.
        """
        ids_df, X_matrix, feature_names = self.preprocessor.isolate_ml_matrix(df_entity_features, id_col="gstin")
        x_tensor = torch.tensor(X_matrix, dtype=torch.float32)

        in_dim = x_tensor.size(1)
        model = ContrastiveProjectionEncoder(in_features=in_dim, hidden_dim=128, proj_dim=self.proj_dim)
        criterion = InfoNCELoss(temperature=self.temperature)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.005)

        model.train()
        for epoch in range(epochs):
            v1, v2 = self.augmentor.generate_views(x_tensor)
            optimizer.zero_grad()

            z1 = model(v1)
            z2 = model(v2)

            loss = criterion(z1, z2)
            loss.backward()
            optimizer.step()

        # Extract refined representations
        model.eval()
        with torch.no_grad():
            refined_embeddings = model(x_tensor).numpy()

        emb_cols = [f"c_emb_{i}" for i in range(self.proj_dim)]
        emb_data = []

        gstins = ids_df["gstin"].tolist()
        for idx, gstin in enumerate(gstins):
            row_dict = {"gstin": gstin}
            for i, col in enumerate(emb_cols):
                row_dict[col] = float(refined_embeddings[idx, i])
            emb_data.append(row_dict)

        df_contrastive = pd.DataFrame(emb_data)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df_contrastive.to_csv(output_path, index=False)

        return df_contrastive
