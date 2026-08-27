"""
CLI Script to Generate Synthetic GST Dataset.
Usage:
    python scripts/generate_data.py --entities 1000 --transactions 10000 --fraud-rate 0.05 --seed 42
"""

import sys
import os
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_generator.generator import GSTDataGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate Synthetic GST Transaction & Fraud Dataset.")
    parser.add_argument("--entities", type=int, default=1000, help="Number of business entities (default: 1000)")
    parser.add_argument("--transactions", type=int, default=10000, help="Number of transactions (default: 10000)")
    parser.add_argument("--fraud-rate", type=float, default=0.05, help="Fraud transaction ratio (default: 0.05)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--output-dir", type=str, default="data/generated", help="Output directory path (default: data/generated)")

    args = parser.parse_args()

    print("==================================================================")
    print(" GST Synthetic Transaction Data Generator")
    print("==================================================================")
    print(f" Entities Target      : {args.entities}")
    print(f" Transactions Target  : {args.transactions}")
    print(f" Target Fraud Rate    : {args.fraud_rate * 100:.1f}%")
    print(f" Random Seed          : {args.seed}")
    print(f" Output Directory     : {args.output_dir}")
    print("==================================================================")

    generator = GSTDataGenerator(seed=args.seed)
    results = generator.generate(
        num_entities=args.entities,
        num_transactions=args.transactions,
        fraud_rate=args.fraud_rate,
        output_dir=args.output_dir
    )

    df_entities = results["entities"]
    df_txs = results["transactions"]
    df_labels = results["fraud_labels"]

    total_txs = len(df_txs)
    fraud_txs = len(df_labels)
    actual_rate = (fraud_txs / total_txs) * 100 if total_txs > 0 else 0.0
    fraud_entities = df_entities["is_fraud_flagged"].sum()

    print("\nGeneration Completed Successfully!")
    print(f" Total Entities Generated   : {len(df_entities)}")
    print(f"   * Flagged Fraud Entities  : {fraud_entities} ({fraud_entities / len(df_entities) * 100:.1f}%)")
    print(f" Total Invoices Generated   : {total_txs}")
    print(f"   * Injected Fraud Invoices: {fraud_txs} ({actual_rate:.2f}%)")
    print("\nFraud Archetype Distribution:")
    if not df_labels.empty:
        pattern_counts = df_labels["fraud_pattern"].value_counts()
        for pattern, count in pattern_counts.items():
            print(f"  * {pattern:20s}: {count:4d} invoices")

    print("\nSaved CSV Files:")
    print(f"  * {os.path.join(args.output_dir, 'entities.csv')}")
    print(f"  * {os.path.join(args.output_dir, 'transactions.csv')}")
    print(f"  * {os.path.join(args.output_dir, 'fraud_labels.csv')}")
    print("==================================================================")

if __name__ == "__main__":
    main()
