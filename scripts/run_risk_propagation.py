"""
Script to run Network Risk Score Propagation Engine.
Usage:
    python scripts/run_risk_propagation.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from ml.propagation.risk_propagation import RiskPropagationEngine

def main():
    direct_risk_path = "data/processed/direct_risk_scores.csv"
    txs_path = "data/generated/transactions.csv"
    output_path = "data/processed/risk_scores.csv"

    if not os.path.exists(direct_risk_path):
        # Fall back to risk_scores if direct_risk_scores not present
        direct_risk_path = "data/processed/risk_scores.csv"

    if not os.path.exists(direct_risk_path):
        print("[ERROR] Risk scores CSV not found. Run: python scripts/train_detector.py")
        sys.exit(1)

    if not os.path.exists(txs_path):
        print("[ERROR] Transactions CSV not found. Run: python scripts/generate_data.py")
        sys.exit(1)

    print("[Propagation] Loading risk scores and transactions...")
    df_risk = pd.read_csv(direct_risk_path)
    df_txs = pd.read_csv(txs_path)

    # Normalize column: support both risk_score and final_risk_score
    if "final_risk_score" in df_risk.columns and "risk_score" not in df_risk.columns:
        df_risk = df_risk.rename(columns={"final_risk_score": "risk_score"})

    engine = RiskPropagationEngine(decay_factor=0.5, max_hops=2)
    print("[Propagation] Running 1-2 hop risk propagation...")
    df_final = engine.propagate_risk(df_risk, df_txs, output_path=output_path)

    high_count = (df_final["risk_category"] == "HIGH").sum()
    med_count = (df_final["risk_category"] == "MEDIUM").sum()
    low_count = (df_final["risk_category"] == "LOW").sum()

    print(f"\n[Propagation] Propagation complete!")
    print(f"  High Risk Entities : {high_count}")
    print(f"  Medium Risk        : {med_count}")
    print(f"  Low Risk           : {low_count}")
    print(f"  Saved to: {output_path}")
    print(f"\n  Top 5 Highest Risk Entities:")
    for _, row in df_final.head(5).iterrows():
        print(f"   {row['anomaly_rank']:>4}  {row['gstin']}  Direct: {row['direct_risk_score']:.1f}  Propagated: {row['propagated_network_risk']:.1f}  Final: {row['final_risk_score']:.1f}  [{row['risk_category']}]")

if __name__ == "__main__":
    main()
