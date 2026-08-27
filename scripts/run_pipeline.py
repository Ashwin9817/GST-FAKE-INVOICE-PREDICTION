"""
Master End-to-End Execution CLI Pipeline Script.
Executes complete pipeline: Data Generation -> Feature Extraction -> GraphSAGE Embeddings -> Contrastive Refinement -> Hybrid Fusion -> Isolation Forest -> Risk Propagation -> Explainable Alerts.
Usage:
    python scripts/run_pipeline.py --entities 500 --transactions 3000 --fraud-rate 0.05 --seed 42
"""

import sys
import os
import argparse
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_generator.generator import GSTDataGenerator
from ml.preprocessing import GSTDataPreprocessor
from ml.feature_engineering import TemporalFeatureExtractor
from graph.graph_features import GraphFeatureExtractor
from ml.gnn.embeddings import GraphEmbeddingGenerator
from ml.contrastive.refinement import ContrastiveRefinementEngine
from ml.fusion.hybrid_fusion import HybridFeatureFusionEngine
from ml.anomaly.isolation_forest import GSTIsolationForestDetector
from ml.anomaly.baselines import BaselineEvaluator
from ml.propagation.risk_propagation import RiskPropagationEngine
from explainability.alert_generator import ExplainableAlertGenerator

def main():
    parser = argparse.ArgumentParser(description="Run End-to-End GST Fraud Detection Pipeline.")
    parser.add_argument("--entities", type=int, default=500, help="Number of entities (default: 500)")
    parser.add_argument("--transactions", type=int, default=3000, help="Number of transactions (default: 3000)")
    parser.add_argument("--fraud-rate", type=float, default=0.05, help="Fraud rate (default: 0.05)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--data-dir", type=str, default="data/generated", help="Raw dataset directory")
    parser.add_argument("--output-dir", type=str, default="data/processed", help="Processed features directory")

    args = parser.parse_args()

    print("==================================================================")
    print(" GST FRAUD DETECTION & RISK INTELLIGENCE PLATFORM")
    print(" Master End-to-End Pipeline Execution")
    print("==================================================================")
    print(f" Entities Target     : {args.entities}")
    print(f" Transactions Target : {args.transactions}")
    print(f" Target Fraud Rate   : {args.fraud_rate * 100:.1f}%")
    print(f" Random Seed         : {args.seed}")
    print("==================================================================")

    # 1. Synthetic Data Generation
    print("\n[STAGE 1/7] Generating Synthetic GST Data & Fraud Archetypes...")
    data_gen = GSTDataGenerator(seed=args.seed)
    gen_results = data_gen.generate(
        num_entities=args.entities,
        num_transactions=args.transactions,
        fraud_rate=args.fraud_rate,
        output_dir=args.data_dir
    )
    df_entities = gen_results["entities"]
    df_txs = gen_results["transactions"]

    # 2. Preprocessing & Feature Extraction
    print("\n[STAGE 2/7] Preprocessing & Extracting Temporal + Graph Features...")
    preprocessor = GSTDataPreprocessor()
    df_txs_clean = preprocessor.clean_transactions(df_txs)

    temp_extractor = TemporalFeatureExtractor()
    df_temporal = temp_extractor.extract_features(df_txs_clean, df_entities)

    graph_extractor = GraphFeatureExtractor()
    df_graph = graph_extractor.extract_features(df_txs_clean, df_entities)

    df_entities_enc = preprocessor.encode_entity_categoricals(df_entities)
    merged_features = pd.merge(df_entities_enc, df_temporal, on="gstin", how="inner")
    merged_features = pd.merge(merged_features, df_graph, on="gstin", how="inner")

    numeric_cols = [
        "total_sales", "total_purchases", "total_turnover", "net_tax_balance",
        "sales_count", "purchases_count", "total_tx_count", "avg_sale", "max_sale",
        "avg_purchase", "max_purchase", "unique_buyers", "unique_suppliers",
        "buyer_supplier_ratio", "tx_per_day", "tx_per_week", "burst_24h_max",
        "rapid_repeat_count", "in_degree", "out_degree", "total_degree",
        "degree_ratio", "pagerank", "community_size", "has_loop", "shortest_loop_dist", "loop_count"
    ]
    df_entity_features = preprocessor.scale_numeric_features(merged_features, numeric_cols, fit=True)
    df_entity_features.to_csv(os.path.join(args.output_dir, "entity_features.csv"), index=False)

    # 3. PyTorch GraphSAGE Node Embedding Learning
    print("\n[STAGE 3/7] Training PyTorch GraphSAGE GNN Embeddings...")
    gnn_gen = GraphEmbeddingGenerator(embedding_dim=64, seed=args.seed)
    df_gnn_embs = gnn_gen.generate_embeddings(
        df_entity_features=df_entity_features,
        df_transactions=df_txs_clean,
        epochs=20,
        output_path=os.path.join(args.output_dir, "gnn_embeddings.csv")
    )

    # 4. Self-Supervised Contrastive Refinement (Novelty #2)
    print("\n[STAGE 4/7] Executing Self-Supervised Contrastive Refinement (Novelty #2)...")
    contrastive_engine = ContrastiveRefinementEngine(proj_dim=64, seed=args.seed)
    df_contrastive = contrastive_engine.train_refine(
        df_entity_features=df_entity_features,
        epochs=20,
        output_path=os.path.join(args.output_dir, "contrastive_embeddings.csv")
    )

    # 5. Hybrid Feature Fusion Engine (Novelty #1)
    print("\n[STAGE 5/7] Executing Feature-Level Hybrid Fusion (Novelty #1)...")
    fusion_engine = HybridFeatureFusionEngine()
    df_fused = fusion_engine.fuse(df_entity_features, df_gnn_embs, output_path=os.path.join(args.output_dir, "fused_features.csv"))

    # 6. Unsupervised Isolation Forest Anomaly Detection
    print("\n[STAGE 6/7] Fitting Isolation Forest & Benchmarking Baselines...")
    detector = GSTIsolationForestDetector(n_estimators=100, contamination=0.1, random_state=args.seed)
    df_direct_risk = detector.train_predict(df_fused, output_path=os.path.join(args.output_dir, "direct_risk_scores.csv"))

    evaluator = BaselineEvaluator()
    df_eval = evaluator.run_comparisons(df_entity_features, df_gnn_embs)

    # 7. Network Risk Score Propagation Engine (Novelty #3) & Explainable Alerts
    print("\n[STAGE 7/7] Executing Network Risk Score Propagation (Novelty #3) & Alert Generator...")
    propagation_engine = RiskPropagationEngine(decay_factor=0.5, max_hops=2)
    df_final_risk = propagation_engine.propagate_risk(
        df_risk_scores=df_direct_risk,
        df_transactions=df_txs_clean,
        output_path=os.path.join(args.output_dir, "risk_scores.csv")
    )

    alert_gen = ExplainableAlertGenerator()
    sample_gstin = df_final_risk.iloc[0]["gstin"]
    sample_risk = df_final_risk.iloc[0].to_dict()
    sample_feat = df_entity_features[df_entity_features["gstin"] == sample_gstin].iloc[0].to_dict()
    sample_explanation = alert_gen.generate_explanation(sample_gstin, sample_risk, sample_feat)

    print("\n==================================================================")
    print(" MASTER PIPELINE COMPLETE - SUMMARY RESULTS")
    print("==================================================================")
    print(f" Total Entities Processed     : {len(df_final_risk)}")
    print(f" Total Invoices Analyzed       : {len(df_txs_clean)}")
    print(f" High Risk Entities (Score>=70): {(df_final_risk['risk_category'] == 'HIGH').sum()}")
    print(f" Medium Risk Entities (40-70) : {(df_final_risk['risk_category'] == 'MEDIUM').sum()}")
    print(f" Low Risk Entities (Score<40)  : {(df_final_risk['risk_category'] == 'LOW').sum()}")
    print("------------------------------------------------------------------")
    print(" Sample High-Risk Explainable Alert Narrative:")
    print(f"  • {sample_explanation['natural_language_summary']}")
    print("==================================================================")

if __name__ == "__main__":
    main()
