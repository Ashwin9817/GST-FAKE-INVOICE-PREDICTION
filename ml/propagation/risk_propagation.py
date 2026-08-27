"""
Network Risk Score Propagation Engine (Proposed Novelty #3).
Propagates time & hop-decayed risk indicators through 1-2 hop supplier-buyer networks.
"""

import os
import pandas as pd
import numpy as np

class RiskPropagationEngine:
    """Propagates decayed risk indicators through 1-hop and 2-hop transaction graph networks."""

    def __init__(self, decay_factor: float = 0.5, max_hops: int = 2):
        self.decay_factor = decay_factor
        self.max_hops = max_hops

    def propagate_risk(
        self,
        df_risk_scores: pd.DataFrame,
        df_transactions: pd.DataFrame,
        output_path: str = None
    ) -> pd.DataFrame:
        """
        Calculates direct anomaly risk, propagated network risk, and integrated final risk indicator.
        Returns DataFrame containing gstin, direct_risk_score, propagated_network_risk, final_risk_score, and category.
        """
        df_risk = df_risk_scores.copy()
        df_tx = df_transactions.copy()

        direct_risk_map = dict(zip(df_risk["gstin"], df_risk["risk_score"]))
        all_gstins = df_risk["gstin"].tolist()

        # Build adjacency mapping (both incoming suppliers and outgoing buyers)
        adj_map = {g: set() for g in all_gstins}
        for _, row in df_tx.iterrows():
            s, b = row["seller_gstin"], row["buyer_gstin"]
            if s in adj_map:
                adj_map[s].add(b)
            if b in adj_map:
                adj_map[b].add(s)

        propagated_map = {g: 0.0 for g in all_gstins}

        # Propagate risk from flagged high-risk entities (> 60 direct risk score)
        high_risk_sources = {g: score for g, score in direct_risk_map.items() if score >= 60.0}

        for source_g, source_risk in high_risk_sources.items():
            # Hop 1 Propagation
            hop1_neighbors = adj_map.get(source_g, set())
            for h1 in hop1_neighbors:
                if h1 != source_g:
                    h1_risk = source_risk * self.decay_factor
                    if h1_risk > propagated_map[h1]:
                        propagated_map[h1] = h1_risk

                    # Hop 2 Propagation
                    if self.max_hops >= 2:
                        hop2_neighbors = adj_map.get(h1, set())
                        for h2 in hop2_neighbors:
                            if h2 != source_g and h2 != h1:
                                h2_risk = source_risk * (self.decay_factor ** 2)
                                if h2_risk > propagated_map[h2]:
                                    propagated_map[h2] = h2_risk

        results = []
        for gstin in all_gstins:
            d_risk = float(direct_risk_map.get(gstin, 0.0))
            p_risk = float(propagated_map.get(gstin, 0.0))
            f_risk = max(d_risk, p_risk)

            if f_risk >= 70.0:
                cat = "HIGH"
            elif f_risk >= 40.0:
                cat = "MEDIUM"
            else:
                cat = "LOW"

            results.append({
                "gstin": gstin,
                "direct_risk_score": round(d_risk, 2),
                "propagated_network_risk": round(p_risk, 2),
                "final_risk_score": round(f_risk, 2),
                "risk_category": cat
            })

        df_out = pd.DataFrame(results).sort_values("final_risk_score", ascending=False).reset_index(drop=True)
        df_out["anomaly_rank"] = [f"#{i + 1}" for i in range(len(df_out))]

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df_out.to_csv(output_path, index=False)

        return df_out
