"""
InfoNCE / NT-Xent Contrastive Loss Function.
Pulls representations of positive augmented entity pairs closer while pushing negative pairs apart.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class InfoNCELoss(nn.Module):
    """InfoNCE (Normalized Temperature-scaled Cross Entropy) Loss."""

    def __init__(self, temperature: float = 0.5):
        super().__init__()
        self.temperature = temperature

    def forward(self, z1: torch.Tensor, z2: torch.Tensor) -> torch.Tensor:
        """
        z1: Normalized embeddings View 1 [N, dim]
        z2: Normalized embeddings View 2 [N, dim]
        """
        N = z1.size(0)

        # L2 Normalize
        z1 = F.normalize(z1, dim=-1)
        z2 = F.normalize(z2, dim=-1)

        # Concatenate views [2N, dim]
        out = torch.cat([z1, z2], dim=0)

        # Cosine similarity matrix [2N, 2N]
        sim_matrix = torch.exp(torch.mm(out, out.t()) / self.temperature)

        # Mask out self-similarity on diagonal
        mask = (~torch.eye(2 * N, dtype=torch.bool, device=z1.device)).float()
        sim_matrix = sim_matrix * mask

        # Positive pairs: (i, i+N) and (i+N, i)
        pos_sim = torch.exp((z1 * z2).sum(dim=-1) / self.temperature)
        pos_sim = torch.cat([pos_sim, pos_sim], dim=0)

        # Contrastive Loss
        loss = -torch.log(pos_sim / (sim_matrix.sum(dim=-1) + 1e-15) + 1e-15).mean()
        return loss
