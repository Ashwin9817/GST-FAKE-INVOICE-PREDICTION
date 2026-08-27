"""
GST Data Preprocessing and Feature Normalization Engine.
Handles missing values, categorical encodings, scaling, and feature isolation.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler, OneHotEncoder

class GSTDataPreprocessor:
    """Preprocessor for GST transactions and business entity features."""

    def __init__(self, scaler_type: str = "robust"):
        self.scaler_type = scaler_type
        if scaler_type == "robust":
            self.scaler = RobustScaler()
        else:
            self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        self.is_fitted = False

    def clean_transactions(self, df_transactions: pd.DataFrame) -> pd.DataFrame:
        """Cleans transaction records, handles missing values, and validates tax math."""
        df = df_transactions.copy()

        # Remove duplicate invoice IDs
        df = df.drop_duplicates(subset=["invoice_id"]).reset_index(drop=True)

        # Parse datetime
        df["invoice_date"] = pd.to_datetime(df["invoice_date"])

        # Fill missing tax values if any
        df["taxable_amount"] = df["taxable_amount"].fillna(0.0)
        df["cgst"] = df["cgst"].fillna(0.0)
        df["sgst"] = df["sgst"].fillna(0.0)
        df["igst"] = df["igst"].fillna(0.0)
        df["total_invoice_amount"] = df["total_invoice_amount"].fillna(df["taxable_amount"] + df["cgst"] + df["sgst"] + df["igst"])

        return df

    def encode_entity_categoricals(self, df_entities: pd.DataFrame) -> pd.DataFrame:
        """Encodes business entity categorical variables (state, size, category)."""
        df = df_entities.copy()
        cat_cols = ["state", "business_size", "category"]

        # Fill missing categoricals
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].fillna("Unknown")

        # Map Business Size to ordinal numeric rank
        size_map = {"Micro": 1, "Small": 2, "Medium": 3, "Large Enterprise": 4}
        if "business_size" in df.columns:
            df["business_size_code"] = df["business_size"].map(size_map).fillna(1).astype(int)

        # One-hot encode state & category
        ohe_cols = [c for c in ["state", "category"] if c in df.columns]
        if ohe_cols:
            ohe_df = pd.get_dummies(df[ohe_cols], prefix=ohe_cols, dtype=float)
            df = pd.concat([df, ohe_df], axis=1)

        return df

    def scale_numeric_features(self, df_features: pd.DataFrame, feature_cols: list[str], fit: bool = True) -> pd.DataFrame:
        """Scales numeric feature columns using RobustScaler or StandardScaler."""
        df = df_features.copy()

        # Fill any NaNs in numeric features with 0
        df[feature_cols] = df[feature_cols].fillna(0.0)

        if fit:
            scaled_vals = self.scaler.fit_transform(df[feature_cols])
            self.is_fitted = True
        else:
            if not self.is_fitted:
                scaled_vals = self.scaler.fit_transform(df[feature_cols])
            else:
                scaled_vals = self.scaler.transform(df[feature_cols])

        for idx, col in enumerate(feature_cols):
            df[f"{col}_scaled"] = scaled_vals[:, idx]

        return df

    def isolate_ml_matrix(self, df_features: pd.DataFrame, id_col: str = "gstin") -> tuple[pd.DataFrame, np.ndarray, list[str]]:
        """
        Separates raw identifier columns from numerical ML feature matrix.
        Returns (df_identifiers, feature_matrix_numpy, feature_names).
        """
        ignore_cols = [id_col, "is_fraud_flagged", "state", "category", "business_size", "fraud_pattern", "state_code"]
        feature_cols = [col for col in df_features.columns if col not in ignore_cols and not col.endswith("_raw")]

        # Filter numeric only columns
        numeric_df = df_features[feature_cols].select_dtypes(include=[np.number])
        final_cols = list(numeric_df.columns)

        identifiers_df = df_features[[col for col in [id_col, "is_fraud_flagged"] if col in df_features.columns]].copy()
        feature_matrix = numeric_df.to_numpy(dtype=np.float32)

        return identifiers_df, feature_matrix, final_cols
