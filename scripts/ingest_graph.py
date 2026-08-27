"""
CLI Script to Ingest Generated CSV Data into Neo4j Graph Database.
Usage:
    python scripts/ingest_graph.py --data-dir data/generated
"""

import sys
import os
import argparse
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph.ingestion import Neo4jGraphIngestor

def main():
    parser = argparse.ArgumentParser(description="Ingest GST dataset into Neo4j graph.")
    parser.add_argument("--data-dir", type=str, default="data/generated", help="Directory containing entities.csv and transactions.csv")
    args = parser.parse_args()

    entities_path = os.path.join(args.data_dir, "entities.csv")
    transactions_path = os.path.join(args.data_dir, "transactions.csv")

    if not os.path.exists(entities_path) or not os.path.exists(transactions_path):
        print(f"Error: Missing dataset CSVs in '{args.data_dir}'. Please run `python scripts/generate_data.py` first.")
        sys.exit(1)

    print("==================================================================")
    print(" Neo4j Graph Ingestion Engine")
    print("==================================================================")
    print(f" Entities Source     : {entities_path}")
    print(f" Transactions Source : {transactions_path}")
    print("==================================================================")

    df_entities = pd.read_csv(entities_path)
    df_txs = pd.read_csv(transactions_path)

    ingestor = Neo4jGraphIngestor()

    print("\n1. Setting up Graph Schema & Indexes...")
    ingestor.setup_schema()

    print("\n2. Ingesting Business Entities...")
    node_count = ingestor.ingest_entities(df_entities)

    print("\n3. Ingesting Transaction Relationships...")
    edge_count = ingestor.ingest_transactions(df_txs)

    stats = ingestor.verify_graph_counts()
    print("\nGraph Ingestion Summary:")
    print(f"  * Node Count Processed : {node_count}")
    print(f"  * Edge Count Processed : {edge_count}")
    print(f"  * Database Status      : {stats['status']}")

    if stats["status"] == "ONLINE":
        print(f"  * Database Nodes       : {stats['node_count']}")
        print(f"  * Database Edges       : {stats['edge_count']}")

    ingestor.close()
    print("==================================================================")

if __name__ == "__main__":
    main()
