"""
Graph Neighborhood & Traversal Service.
"""

import os
import pandas as pd
from backend.app.config import settings

class GraphService:
    """Service building 1-hop and 2-hop transaction network subgraphs for visualization."""

    def __init__(self):
        self._load_data()

    def _load_data(self):
        if os.path.exists(settings.TRANSACTIONS_FILE):
            self.df_txs = pd.read_csv(settings.TRANSACTIONS_FILE)
        else:
            self.df_txs = pd.DataFrame()

        if os.path.exists(settings.ENTITIES_FILE):
            self.df_entities = pd.read_csv(settings.ENTITIES_FILE)
        else:
            self.df_entities = pd.DataFrame()

    def get_network_subgraph(self, gstin: str, hops: int = 1) -> dict:
        """
        Extracts 1-hop or 2-hop directed graph neighborhood around specified GSTIN.
        Returns JSON representation: {"nodes": [...], "edges": [...]}.
        """
        self._load_data()
        center = gstin.upper().strip()

        if self.df_txs.empty:
            return {"nodes": [{"id": center, "label": center, "type": "center"}], "edges": []}

        # 1-Hop edges (direct transactions with center)
        hop1_txs = self.df_txs[
            (self.df_txs["seller_gstin"] == center) | (self.df_txs["buyer_gstin"] == center)
        ].copy()

        hop1_nodes = set(hop1_txs["seller_gstin"]).union(set(hop1_txs["buyer_gstin"]))
        hop1_nodes.discard(center)

        all_txs = hop1_txs

        # 2-Hop edges if requested
        if hops >= 2 and len(hop1_nodes) > 0:
            hop2_txs = self.df_txs[
                ((self.df_txs["seller_gstin"].isin(hop1_nodes)) | (self.df_txs["buyer_gstin"].isin(hop1_nodes)))
                & (self.df_txs["seller_gstin"] != center)
                & (self.df_txs["buyer_gstin"] != center)
            ].copy()
            all_txs = pd.concat([hop1_txs, hop2_txs]).drop_duplicates(subset=["invoice_id"])

        # Build edge list and keep track of nodes that have at least 1 edge
        edges_list = []
        nodes_with_edges = set([center])
        for _, row in all_txs.iterrows():
            s = str(row["seller_gstin"]).strip().upper()
            t = str(row["buyer_gstin"]).strip().upper()
            edges_list.append({
                "id": str(row["invoice_id"]),
                "source": s,
                "target": t,
                "amount": float(row.get("total_invoice_amount", 0.0)),
                "fraud_pattern": str(row.get("fraud_pattern", "NONE"))
            })
            nodes_with_edges.add(s)
            nodes_with_edges.add(t)

        # Load risk scores dictionary for node risk mapping
        risk_map = {}
        risk_file = os.path.join(settings.DATA_DIR, "processed", "risk_scores.csv")
        if os.path.exists(risk_file):
            try:
                df_risk = pd.read_csv(risk_file)
                for _, r_row in df_risk.iterrows():
                    risk_map[str(r_row["gstin"]).upper()] = {
                        "risk_category": str(r_row.get("risk_category", "LOW")),
                        "risk_score": float(r_row.get("final_risk_score", r_row.get("risk_score", 0.0)))
                    }
            except Exception:
                pass

        # Only include nodes that actually have edges in the network
        nodes_list = []
        for n in nodes_with_edges:
            n_type = "center" if n == center else ("hop1" if n in hop1_nodes else "hop2")
            r_info = risk_map.get(n, {"risk_category": "LOW", "risk_score": 0.0})
            nodes_list.append({
                "id": n,
                "label": n,
                "type": n_type,
                "risk_category": r_info["risk_category"],
                "risk_score": r_info["risk_score"]
            })

        return {
            "center_gstin": center,
            "hops": hops,
            "nodes": nodes_list,
            "edges": edges_list
        }
