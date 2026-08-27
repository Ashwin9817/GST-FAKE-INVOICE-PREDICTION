"""
Risk Intelligence & Entity Profile Service.
Enhanced with propagated risk scores, high-risk ranking, and robust column handling.
"""

import os
import pandas as pd
from backend.app.config import settings


class RiskService:
    """Service serving entity risk scores, transaction logs, and profile statistics."""

    def __init__(self):
        self._load_data()

    def _load_data(self):
        """Loads entities, transactions, and risk score CSV files if available."""
        self.df_entities = pd.read_csv(settings.ENTITIES_FILE) if os.path.exists(settings.ENTITIES_FILE) else pd.DataFrame()
        self.df_txs = pd.read_csv(settings.TRANSACTIONS_FILE) if os.path.exists(settings.TRANSACTIONS_FILE) else pd.DataFrame()
        self.df_risk = pd.read_csv(settings.RISK_SCORES_FILE) if os.path.exists(settings.RISK_SCORES_FILE) else pd.DataFrame()
        self.df_features = pd.read_csv(settings.ENTITY_FEATURES_FILE) if os.path.exists(settings.ENTITY_FEATURES_FILE) else pd.DataFrame()

    def get_system_stats(self) -> dict:
        """Returns overall system platform statistics."""
        self._load_data()
        total_entities = len(self.df_entities)
        total_txs = len(self.df_txs)

        if not self.df_risk.empty and "risk_category" in self.df_risk.columns:
            high_risk = int((self.df_risk["risk_category"] == "HIGH").sum())
            med_risk = int((self.df_risk["risk_category"] == "MEDIUM").sum())
            low_risk = int((self.df_risk["risk_category"] == "LOW").sum())
        else:
            high_risk = med_risk = low_risk = 0

        # Average and max risk score
        avg_risk = 0.0
        max_risk = 0.0
        risk_col = None
        for col in ["final_risk_score", "risk_score"]:
            if not self.df_risk.empty and col in self.df_risk.columns:
                risk_col = col
                break
        if risk_col:
            avg_risk = round(float(self.df_risk[risk_col].mean()), 2)
            max_risk = round(float(self.df_risk[risk_col].max()), 2)

        return {
            "total_entities": total_entities,
            "total_transactions": total_txs,
            "high_risk_count": high_risk,
            "medium_risk_count": med_risk,
            "low_risk_count": low_risk,
            "average_risk_score": avg_risk,
            "max_risk_score": max_risk,
            "detected_fraud_patterns": ["CIRCULAR_TRADING", "STAR_COLLUSION", "SPLIT_INVOICING", "HIGH_VELOCITY"]
        }

    def get_entity_profile(self, gstin: str) -> dict:
        """Returns detailed entity profile, topological parameters, and risk metrics."""
        self._load_data()
        gstin_clean = gstin.upper().strip()

        entity_row = self.df_entities[self.df_entities["gstin"] == gstin_clean] if not self.df_entities.empty else pd.DataFrame()
        if entity_row.empty:
            return {"error": f"GSTIN '{gstin_clean}' not found in database."}

        entity_info = entity_row.iloc[0].to_dict()

        # Risk score info — handles both old (risk_score) and new (final_risk_score) schema
        risk_info = {"risk_score": 15.0, "final_risk_score": 15.0, "risk_category": "LOW", "anomaly_rank": "#N/A", "direct_risk_score": 15.0, "propagated_network_risk": 0.0}
        if not self.df_risk.empty and "gstin" in self.df_risk.columns:
            r_row = self.df_risk[self.df_risk["gstin"] == gstin_clean]
            if not r_row.empty:
                risk_info = r_row.iloc[0].to_dict()
                # Ensure backward-compat alias
                if "risk_score" not in risk_info and "final_risk_score" in risk_info:
                    risk_info["risk_score"] = risk_info["final_risk_score"]

        # Topological feature info
        feat_info = {}
        if not self.df_features.empty and "gstin" in self.df_features.columns:
            f_row = self.df_features[self.df_features["gstin"] == gstin_clean]
            if not f_row.empty:
                feat_info = f_row.iloc[0].to_dict()

        return {
            "entity": entity_info,
            "risk": risk_info,
            "features": feat_info
        }

    def get_entity_transactions(self, gstin: str, limit: int = 50) -> list:
        """Returns transaction log history for specified entity with counterparty risk enrichment."""
        self._load_data()
        gstin_clean = gstin.upper().strip()

        if self.df_txs.empty:
            return []

        # Create quick risk lookup dict
        risk_lookup = {}
        if not self.df_risk.empty and "gstin" in self.df_risk.columns:
            for _, r_row in self.df_risk.iterrows():
                risk_lookup[str(r_row["gstin"]).upper()] = {
                    "category": str(r_row.get("risk_category", "LOW")),
                    "score": float(r_row.get("final_risk_score", r_row.get("risk_score", 0.0)))
                }

        s_txs = self.df_txs[self.df_txs["seller_gstin"] == gstin_clean].copy()
        s_txs["direction"] = "OUTGOING"
        s_txs["counterparty"] = s_txs["buyer_gstin"]

        b_txs = self.df_txs[self.df_txs["buyer_gstin"] == gstin_clean].copy()
        b_txs["direction"] = "INCOMING"
        b_txs["counterparty"] = b_txs["seller_gstin"]

        combined = pd.concat([s_txs, b_txs]).sort_values("invoice_date", ascending=False).head(limit)

        records = combined.fillna("").to_dict(orient="records")
        for r in records:
            c_gstin = str(r.get("counterparty", "")).upper()
            c_info = risk_lookup.get(c_gstin, {"category": "LOW", "score": 0.0})
            r["counterparty_risk_category"] = c_info["category"]
            r["counterparty_risk_score"] = c_info["score"]

        return records

    def get_high_risk_entities(self, limit: int = 20) -> list:
        """Returns top N entities ranked by final risk score descending."""
        self._load_data()

        if self.df_risk.empty:
            return []

        risk_col = "final_risk_score" if "final_risk_score" in self.df_risk.columns else "risk_score"
        df_sorted = self.df_risk.sort_values(risk_col, ascending=False).head(limit)
        return df_sorted.fillna("").to_dict(orient="records")

    def verify_msme_supplier(self, supplier_gstin: str) -> dict:
        """Verifies supplier risk status for MSME buyers."""
        profile = self.get_entity_profile(supplier_gstin)
        if "error" in profile:
            return {
                "supplier_gstin": supplier_gstin,
                "status": "NOT_FOUND",
                "risk_category": "UNKNOWN",
                "risk_score": 0.0,
                "warnings": [],
                "message": "GSTIN not found in GST database. Request official registration certificate."
            }

        risk_cat = profile["risk"].get("risk_category", "LOW")
        risk_score = profile["risk"].get("final_risk_score", profile["risk"].get("risk_score", 15.0))
        propagated = profile["risk"].get("propagated_network_risk", 0.0)

        warnings = []
        if risk_cat == "HIGH":
            warnings.append("Supplier participates in anomalous transaction graph structures.")
            warnings.append("Elevated transaction velocity or sub-threshold invoice splitting detected.")
            if propagated >= 30:
                warnings.append(f"Network-propagated risk from connected high-risk entities ({propagated:.1f}/100).")
            recommendation = "CAUTION: Verify physical delivery of goods and E-Way bills before releasing payments or claiming ITC."
        elif risk_cat == "MEDIUM":
            warnings.append("Moderate transactional variance detected.")
            if propagated > 0:
                warnings.append(f"Indirect network exposure detected ({propagated:.1f}/100).")
            recommendation = "NEUTRAL: Conduct standard commercial verification before transacting."
        else:
            recommendation = "SAFE TO TRANSACT: Supplier displays clean transactional and topological behavior."

        return {
            "supplier_gstin": supplier_gstin,
            "status": "VERIFIED",
            "risk_category": risk_cat,
            "risk_score": round(float(risk_score), 2),
            "propagated_network_risk": round(float(propagated), 2),
            "warnings": warnings,
            "recommendation": recommendation
        }
