"""
CLI Script to Fuse Features, Train Isolation Forest Anomaly Detector, and Benchmark Baselines.
Usage:
    python scripts/train_detector.py
"""

import sys
import os
import argparse
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.fusion.hybrid_fusion import HybridFeatureFusionEngine
from ml.anomaly.isolation_forest import GSTIsolationForestDetector
from ml.anomaly.baselines import BaselineEvaluator

def main():
    parser = argparse.ArgumentParser(description="Train Isolation Forest Anomaly Detector & Benchmark Baselines.")
    parser.add_argument("--entity-features", type=str, default="data/processed/entity_features.csv", help="Entity features CSV")
    parser.add_argument("--gnn-embeddings", type=str, default="data/processed/gnn_embeddings.csv", help="GraphSAGE embeddings CSV")
    parser.add_argument("--fused-output", type=str, default="data/processed/fused_features.csv", help="Fused features output path")
    parser.add_argument("--risk-output", type=str, default="data/processed/risk_scores.csv", help="Risk scores output path")

    args = parser.parse_args()

    if not os.path.exists(args.entity_features) or not os.path.exists(args.gnn_embeddings):
        print("Error: Missing feature files. Please run `python scripts/extract_features.py` and `python scripts/train_gnn.py` first.")
        sys.exit(1)

    print("==================================================================")
    print(" GST Isolation Forest Anomaly Detector & Fusion Engine")
    print("==================================================================")
    print(f" Entity Features : {args.entity_features}")
    print(f" GNN Embeddings  : {args.gnn_embeddings}")
    print("==================================================================")

    df_entity_features = pd.read_csv(args.entity_features)
    df_gnn_embeddings = pd.read_csv(args.gnn_embeddings)

    # 1. Feature Fusion (Proposed Novelty #1)
    print("\n1. Executing Feature-Level Hybrid Fusion...")
    fusion_engine = HybridFeatureFusionEngine()
    df_fused = fusion_engine.fuse(df_entity_features, df_gnn_embeddings, output_path=args.fused_output)
    print(f"   * Fused Feature Matrix Saved: {args.fused_output} ({len(df_fused)} rows, {len(df_fused.columns)} columns)")

    # 2. Fit Isolation Forest & Calculate 0-100 Risk Scores
    print("\n2. Fitting Unsupervised Isolation Forest Anomaly Detector...")
    detector = GSTIsolationForestDetector(n_estimators=100, contamination=0.1, random_state=42)
    df_risk = detector.train_predict(df_fused, output_path=args.risk_output)

    high_risk_count = (df_risk["risk_category"] == "HIGH").sum()
    med_risk_count = (df_risk["risk_category"] == "MEDIUM").sum()
    low_risk_count = (df_risk["risk_category"] == "LOW").sum()

    print(f"   * Risk Score Normalization Complete (Saved: {args.risk_output})")
    print(f"   * Risk Distribution: High={high_risk_count}, Medium={med_risk_count}, Low={low_risk_count}")

    # 3. Benchmark Baseline Models against Ground-Truth Evaluation Labels
    print("\n3. Running Comparative Baseline Evaluation Experiments...")
    evaluator = BaselineEvaluator()
    df_results = evaluator.run_comparisons(df_entity_features, df_gnn_embeddings)

    print("\n==================================================================")
    print(" MODEL PERFORMANCE & BASELINE EVALUATION COMPARISON")
    print("==================================================================")
    for _, row in df_results.iterrows():
        print(f" Model: {row['model_name']}")
        print(f"   • Accuracy  : {row['accuracy']:.4f} ({row['accuracy']*100:.2f}%)")
        print(f"   • Precision : {row['precision']:.4f} ({row['precision']*100:.2f}%)")
        print(f"   • Recall    : {row['recall']:.4f} ({row['recall']*100:.2f}%)")
        print(f"   • F1-Score  : {row['f1']:.4f}")
        print(f"   • ROC-AUC   : {row['roc_auc']:.4f}")
        print(f"   • PR-AUC    : {row['pr_auc']:.4f}")
        print("------------------------------------------------------------------")
    print("==================================================================")

if __name__ == "__main__":
    main()
