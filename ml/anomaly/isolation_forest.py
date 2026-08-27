"""
Isolation Forest Unsupervised Anomaly Detection Module.
Fits Isolation Forest on hybrid features and maps raw decision function scores into normalized 0-100 Risk Scores.
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from ml.preprocessing import GSTDataPreprocessor

class GSTIsolationForestDetector:
    """Unsupervised Isolation Forest Detector with 0-100 Risk Score Normalization."""

    def __init__(
        self,
        n_estimators: int = 100,
        contamination: float = 0.1,
        random_state: int = 42
    ):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )
        self.preprocessor = GSTDataPreprocessor()
        self.is_fitted = False

    def train_predict(self, df_fused_features: pd.DataFrame, output_path: str = None) -> pd.DataFrame:
        """
        Fits Isolation Forest on fused numerical features.
        Returns DataFrame containing gstin, raw_score, risk_score, risk_category, and anomaly_rank.
        """
        df = df_fused_features.copy()

        # Isolate numerical features (excluding IDs and labels)
        ids_df, X_matrix, feature_names = self.preprocessor.isolate_ml_matrix(df, id_col="gstin")

        # Fit Isolation Forest
        self.model.fit(X_matrix)
        self.is_fitted = True

        # Compute raw decision function score (lower values = higher anomaly)
        raw_scores = self.model.decision_function(X_matrix)
        anomaly_flags = self.model.predict(X_matrix)  # -1 for anomaly, 1 for normal

        # Convert raw decision scores into an interpretable 0 - 100 Risk Score
        # Raw decision_function typically ranges from -0.3 to +0.3
        # We invert and scale so that anomalous entities (negative raw scores) receive high risk scores (close to 100)
        min_raw = min(raw_scores)
        max_raw = max(raw_scores)

        if max_raw > min_raw:
            # Linear inversion to 0 - 100 range
            normalized_risk = 100.0 * (1.0 - (raw_scores - min_raw) / (max_raw - min_raw))
        else:
            normalized_risk = np.full_like(raw_scores, 50.0)

        results_df = df[["gstin"]].copy()
        if "is_fraud_flagged" in df.columns:
            results_df["is_fraud_flagged"] = df["is_fraud_flagged"]

        results_df["raw_anomaly_score"] = raw_scores
        results_df["risk_score"] = np.round(normalized_risk, 2)
        results_df["anomaly_flag"] = np.where(anomaly_flags == -1, 1, 0)

        # Assign Risk Category Badges
        def categorize_risk(score):
            if score >= 70.0:
                return "HIGH"
            elif score >= 40.0:
                return "MEDIUM"
            else:
                return "LOW"

        results_df["risk_category"] = results_df["risk_score"].apply(categorize_risk)

        # Sort by risk score descending to assign anomaly ranks
        results_df = results_df.sort_values(by="risk_score", ascending=False).reset_index(drop=True)
        results_df["anomaly_rank"] = [f"#{i + 1}" for i in range(len(results_df))]

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            results_df.to_csv(output_path, index=False)

        return results_df
