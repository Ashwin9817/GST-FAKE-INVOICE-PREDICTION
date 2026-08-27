"""
Baseline Comparison Engine.
Evaluates Isolation Forest on:
- Baseline 1: Transactional features only
- Baseline 2: Transactional + Manual Graph features
- Proposed: Hybrid Feature Fusion (Transactional + Graph + GraphSAGE Embeddings)
Calculates Precision, Recall, F1-Score, ROC-AUC, and PR-AUC.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, precision_recall_curve, auc
from ml.preprocessing import GSTDataPreprocessor

class BaselineEvaluator:
    """Evaluates Isolation Forest accuracy across feature combinations."""

    def __init__(self):
        self.preprocessor = GSTDataPreprocessor()

    def evaluate_model(self, X_matrix: np.ndarray, y_true: np.ndarray, model_name: str) -> dict:
        """Fits Isolation Forest and calculates evaluation metrics against ground-truth labels."""
        if len(X_matrix) == 0 or len(y_true) == 0:
            return {"model_name": model_name, "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "roc_auc": 0.0, "pr_auc": 0.0}

        # Dynamic contamination rate based on ground-truth ratio
        fraud_ratio = float(np.mean(y_true))
        contamination = max(0.01, min(0.5, fraud_ratio if fraud_ratio > 0 else 0.1))

        model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
        model.fit(X_matrix)

        raw_scores = model.decision_function(X_matrix)
        pred_labels = np.where(model.predict(X_matrix) == -1, 1, 0)
        score_probs = 1.0 - (raw_scores - min(raw_scores)) / (max(raw_scores) - min(raw_scores) + 1e-15)

        # Calculate metrics
        from sklearn.metrics import accuracy_score
        acc = float(accuracy_score(y_true, pred_labels))
        prec = float(precision_score(y_true, pred_labels, zero_division=0))
        rec = float(recall_score(y_true, pred_labels, zero_division=0))
        f1 = float(f1_score(y_true, pred_labels, zero_division=0))

        try:
            roc_auc = float(roc_auc_score(y_true, score_probs))
        except Exception:
            roc_auc = 0.5

        try:
            p_curve, r_curve, _ = precision_recall_curve(y_true, score_probs)
            pr_auc = float(auc(r_curve, p_curve))
        except Exception:
            pr_auc = 0.5

        return {
            "model_name": model_name,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4)
        }

    def run_comparisons(
        self,
        df_entity_features: pd.DataFrame,
        df_gnn_embeddings: pd.DataFrame
    ) -> pd.DataFrame:
        """Runs comparative experiment across Baseline 1, Baseline 2, and Proposed Hybrid Fusion."""
        df_merged = pd.merge(df_entity_features, df_gnn_embeddings, on="gstin", how="inner")
        y_true = df_merged["is_fraud_flagged"].to_numpy(dtype=int)

        # 1. Baseline 1: Transactional Features Only
        tx_cols = [c for c in df_merged.columns if any(k in c for k in ["sales", "purchase", "turnover", "tx_per", "burst"])]
        if not tx_cols:
            tx_cols = ["sales_count", "purchases_count"]
        X_tx = df_merged[tx_cols].select_dtypes(include=[np.number]).fillna(0.0).to_numpy()
        res_b1 = self.evaluate_model(X_tx, y_true, "Baseline 1 (Transactional Only)")

        # 2. Baseline 2: Transactional + Manual Graph Topology
        graph_cols = [c for c in df_merged.columns if any(k in c for k in ["pagerank", "degree", "loop", "community"])]
        X_tx_graph = df_merged[tx_cols + graph_cols].select_dtypes(include=[np.number]).fillna(0.0).to_numpy()
        res_b2 = self.evaluate_model(X_tx_graph, y_true, "Baseline 2 (Transactional + Graph Topology)")

        # 3. Proposed: Hybrid Feature Fusion (Transactional + Graph Topology + GraphSAGE Embeddings)
        ids_df, X_fused, _ = self.preprocessor.isolate_ml_matrix(df_merged, id_col="gstin")
        res_prop = self.evaluate_model(X_fused, y_true, "Proposed (Hybrid Fusion + GraphSAGE Embeddings)")

        return pd.DataFrame([res_b1, res_b2, res_prop])
