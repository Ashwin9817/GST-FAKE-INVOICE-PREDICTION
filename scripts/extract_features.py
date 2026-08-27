"""
CLI Script to Extract Temporal and Graph Topological Features.
Usage:
    python scripts/extract_features.py --data-dir data/generated --output-dir data/processed
"""

import sys
import os
import argparse
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.feature_engineering import TemporalFeatureExtractor
from graph.graph_features import GraphFeatureExtractor
from ml.preprocessing import GSTDataPreprocessor

def main():
    parser = argparse.ArgumentParser(description="Extract Temporal and Graph Features for GST Entities.")
    parser.add_argument("--data-dir", type=str, default="data/generated", help="Directory containing entities.csv and transactions.csv")
    parser.add_argument("--output-dir", type=str, default="data/processed", help="Output directory for processed feature matrices")

    args = parser.parse_args()

    entities_path = os.path.join(args.data_dir, "entities.csv")
    transactions_path = os.path.join(args.data_dir, "transactions.csv")

    if not os.path.exists(entities_path) or not os.path.exists(transactions_path):
        print(f"Error: Missing CSVs in '{args.data_dir}'. Run `python scripts/generate_data.py` first.")
        sys.exit(1)

    print("==================================================================")
    print(" GST Feature Engineering & Topological Extraction Pipeline")
    print("==================================================================")
    print(f" Reading Entities     : {entities_path}")
    print(f" Reading Transactions : {transactions_path}")
    print("==================================================================")

    df_entities = pd.read_csv(entities_path)
    df_txs = pd.read_csv(transactions_path)

    # 1. Clean transactions
    preprocessor = GSTDataPreprocessor()
    df_txs_clean = preprocessor.clean_transactions(df_txs)

    # 2. Extract Temporal Features
    print("\n1. Extracting Entity Temporal & Financial Metrics...")
    temporal_extractor = TemporalFeatureExtractor()
    df_temporal = temporal_extractor.extract_features(df_txs_clean, df_entities)
    print(f"   * Processed {len(df_temporal)} entity temporal feature vectors.")

    # 3. Extract Graph Topological Features
    print("\n2. Extracting Graph Topology (PageRank, Louvain, Loops)...")
    graph_extractor = GraphFeatureExtractor()
    df_graph = graph_extractor.extract_features(df_txs_clean, df_entities)
    print(f"   * Processed {len(df_graph)} entity graph topology vectors.")

    # 4. Merge All Features
    print("\n3. Merging Entity Features & Normalizing Categoricals...")
    df_entities_enc = preprocessor.encode_entity_categoricals(df_entities)

    merged = pd.merge(df_entities_enc, df_temporal, on="gstin", how="inner")
    merged = pd.merge(merged, df_graph, on="gstin", how="inner")

    # 5. Scale Numeric Feature Columns
    numeric_cols = [
        "total_sales", "total_purchases", "total_turnover", "net_tax_balance",
        "sales_count", "purchases_count", "total_tx_count", "avg_sale", "max_sale",
        "avg_purchase", "max_purchase", "unique_buyers", "unique_suppliers",
        "buyer_supplier_ratio", "tx_per_day", "tx_per_week", "burst_24h_max",
        "rapid_repeat_count", "in_degree", "out_degree", "total_degree",
        "degree_ratio", "pagerank", "community_size", "has_loop", "shortest_loop_dist", "loop_count"
    ]

    df_scaled = preprocessor.scale_numeric_features(merged, numeric_cols, fit=True)

    os.makedirs(args.output_dir, exist_ok=True)
    out_file = os.path.join(args.output_dir, "entity_features.csv")
    df_scaled.to_csv(out_file, index=False)

    print("\nFeature Extraction Summary:")
    print(f"  * Total Entity Features Table Rows: {len(df_scaled)}")
    print(f"  * Total Extracted Feature Columns  : {len(df_scaled.columns)}")
    print(f"  * Saved Processed Feature Matrix   : {out_file}")
    print("==================================================================")

if __name__ == "__main__":
    main()
