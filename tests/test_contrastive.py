"""
Unit Tests for Self-Supervised Contrastive Refinement Engine.
"""

import unittest
import torch
import pandas as pd
from ml.contrastive.augmentations import ContrastiveAugmentor
from ml.contrastive.loss import InfoNCELoss
from ml.contrastive.refinement import ContrastiveRefinementEngine

class TestContrastiveRefinement(unittest.TestCase):

    def setUp(self):
        self.augmentor = ContrastiveAugmentor(seed=42)
        self.loss_fn = InfoNCELoss(temperature=0.5)
        self.x = torch.randn(10, 16)

    def test_augmentations(self):
        v1, v2 = self.augmentor.generate_views(self.x)
        self.assertEqual(v1.shape, self.x.shape)
        self.assertEqual(v2.shape, self.x.shape)

    def test_infonce_loss(self):
        v1, v2 = self.augmentor.generate_views(self.x)
        loss = self.loss_fn(v1, v2)
        self.assertTrue(torch.is_tensor(loss))
        self.assertFalse(torch.isnan(loss))
        self.assertGreater(float(loss), 0.0)

    def test_contrastive_refinement_engine(self):
        df_feat = pd.DataFrame([
            {"gstin": "A", "val1": 1.0, "val2": 2.0},
            {"gstin": "B", "val1": 3.0, "val2": 4.0}
        ])
        engine = ContrastiveRefinementEngine(proj_dim=32, seed=42)
        df_c = engine.train_refine(df_feat, epochs=5)
        self.assertEqual(len(df_c), 2)
        self.assertIn("c_emb_0", df_c.columns)

if __name__ == "__main__":
    unittest.main()
