"""
CLI Script to Train GraphSAGE GNN and Extract Node Embeddings.
Usage:
    python scripts/train_gnn.py --epochs 30
"""

import sys
import os
import argparse
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.gnn.embeddings import GraphEmbeddingGenerator

def main():
    parser = argparse.ArgumentParser(description="Train GraphSAGE GNN and Extract Node Embeddings.")
    parser.add_argument("--features-file", type=str, default="data/processed/entity_features.csv", help="Processed entity features CSV")
    parser.add_argument("--transactions-file", type=str, default="data/generated/transactions.csv", help="Transactions CSV")
    parser.add_argument("--output-file", type=str, default="data/processed/gnn_embeddings.csv", help="Output embeddings CSV path")
    parser.add_argument("--epochs", type=int, default=30, help="Training epochs (default: 30)")
    parser.add_argument("--embedding-dim", type=int, default=64, help="Embedding dimension (default: 64)")

    args = parser.parse_args()

    if not os.path.exists(args.features_file) or not os.path.exists(args.transactions_file):
        print("Error: Missing feature files. Please run `python scripts/extract_features.py` first.")
        sys.exit(1)

    print("==================================================================")
    print(" PyTorch GraphSAGE Embedding Generator")
    print("==================================================================")
    print(f" Reading Entity Features : {args.features_file}")
    print(f" Reading Transactions     : {args.transactions_file}")
    print(f" Training Epochs          : {args.epochs}")
    print(f" Target Embedding Dim     : {args.embedding_dim}")
    print("==================================================================")

    df_features = pd.read_csv(args.features_file)
    df_txs = pd.read_csv(args.transactions_file)

    generator = GraphEmbeddingGenerator(embedding_dim=args.embedding_dim)
    df_embeddings = generator.generate_embeddings(
        df_entity_features=df_features,
        df_transactions=df_txs,
        epochs=args.epochs,
        output_path=args.output_file
    )

    print("\nGraphSAGE Embedding Generation Completed!")
    print(f" Total Entity Embeddings Generated : {len(df_embeddings)}")
    print(f" Embedding Dimension               : {args.embedding_dim}")
    print(f" Saved Graph Embeddings Matrix     : {args.output_file}")
    print("==================================================================")

if __name__ == "__main__":
    main()
