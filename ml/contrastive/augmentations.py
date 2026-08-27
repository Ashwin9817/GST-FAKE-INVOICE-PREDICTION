"""
Graph / Feature Augmentations for Self-Supervised Contrastive Learning.
Generates dual representation views via feature masking and Gaussian noise perturbation.
"""

import torch

class ContrastiveAugmentor:
    """Generates dual augmented feature views for self-supervised representation refinement."""

    def __init__(self, mask_ratio: float = 0.15, noise_std: float = 0.05, seed: int = 42):
        self.mask_ratio = mask_ratio
        self.noise_std = noise_std
        torch.manual_seed(seed)

    def generate_views(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Generates View 1 (Feature Masking) and View 2 (Gaussian Noise Perturbation).
        x: [num_nodes, feature_dim]
        Returns: (v1, v2)
        """
        # View 1: Feature Masking
        mask1 = torch.rand_like(x) > self.mask_ratio
        v1 = x * mask1.float()

        # View 2: Gaussian Noise Perturbation
        noise = torch.randn_like(x) * self.noise_std
        v2 = x + noise

        return v1, v2
