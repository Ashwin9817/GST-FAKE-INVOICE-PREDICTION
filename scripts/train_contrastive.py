"""
Script to train contrastive representation refinement on entity features.
Usage:
    python scripts/train_contrastive.py --epochs 25
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
import pandas as pd
from ml.contrastive.refinement import ContrastiveRefinementEngine

def main():
    parser = argparse.ArgumentParser(description="Train Self-Supervised Contrastive Representation Refinement.")
    parser.add_argument("--features", type=str, default="data/processed/entity_features.csv")
    parser.add_argument("--output", type=str, default="data/processed/contrastive_embeddings.csv")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--proj-dim", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not os.path.exists(args.features):
        print(f"[ERROR] Entity features not found at: {args.features}")
        print("  Run first: python scripts/extract_features.py")
        sys.exit(1)

    print(f"[Contrastive] Loading features from: {args.features}")
    df_features = pd.read_csv(args.features)

    print(f"[Contrastive] Training with proj_dim={args.proj_dim}, epochs={args.epochs}, seed={args.seed}")
    engine = ContrastiveRefinementEngine(proj_dim=args.proj_dim, seed=args.seed)
    df_embs = engine.train_refine(df_features, epochs=args.epochs, output_path=args.output)

    print(f"[Contrastive] Done. Contrastive embeddings shape: {df_embs.shape}")
    print(f"[Contrastive] Saved to: {args.output}")

if __name__ == "__main__":
    main()
