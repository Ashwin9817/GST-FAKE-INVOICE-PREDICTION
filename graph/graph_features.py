"""
Graph Topological Feature Extraction Engine.
Calculates PageRank centrality, Louvain community partitions, degree distributions, and 3-6 hop circular loop closures.
"""

import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms.community import louvain_communities

class GraphFeatureExtractor:
    """Extracts topological graph features from business transaction edges."""

    def __init__(self, damping_factor: float = 0.85):
        self.damping_factor = damping_factor

    def build_networkx_graph(self, df_transactions: pd.DataFrame, df_entities: pd.DataFrame) -> nx.DiGraph:
        """Constructs a directed multigraph / weighted graph from transaction edges."""
        G = nx.DiGraph()

        # Add all entity nodes
        for gstin in df_entities["gstin"]:
            G.add_node(gstin)

        # Aggregate transaction weights between seller -> buyer pairs
        edge_weights = df_transactions.groupby(["seller_gstin", "buyer_gstin"]).agg(
            weight=("total_invoice_amount", "sum"),
            tx_count=("invoice_id", "count")
        ).reset_index()

        for _, row in edge_weights.iterrows():
            G.add_edge(
                row["seller_gstin"],
                row["buyer_gstin"],
                weight=float(row["weight"]),
                tx_count=int(row["tx_count"])
            )

        return G

    def extract_features(self, df_transactions: pd.DataFrame, df_entities: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts node-level graph features: PageRank, Degree, Louvain Community, and Loop Closures.
        Returns DataFrame indexed by GSTIN.
        """
        G = self.build_networkx_graph(df_transactions, df_entities)

        # 1. PageRank Centrality
        try:
            pagerank_map = nx.pagerank(G, weight="weight", alpha=self.damping_factor)
        except Exception:
            # Fallback uniform PageRank if convergence fails
            pagerank_map = {node: 1.0 / max(1, len(G.nodes)) for node in G.nodes}

        # 2. Degree Features
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())

        # 3. Louvain Community Detection
        # Convert to undirected for community partition
        G_undirected = G.to_undirected()
        try:
            communities = louvain_communities(G_undirected, seed=42)
        except Exception:
            communities = [set(G.nodes)]

        community_map = {}
        community_size_map = {}
        for c_idx, comm in enumerate(communities):
            c_name = f"COMM_{c_idx + 1:03d}"
            c_size = len(comm)
            for node in comm:
                community_map[node] = c_name
                community_size_map[node] = c_size

        # 4. Circular Loop Closure Detection (3-6 Hops)
        # Cap cycle enumeration to avoid exponential blowup on dense graphs
        MAX_CYCLES = 500
        cycle_info_map = {node: {"has_loop": 0, "shortest_dist": 0, "loop_count": 0} for node in G.nodes}
        try:
            count = 0
            for c in nx.simple_cycles(G):
                if count >= MAX_CYCLES:
                    break
                c_len = len(c)
                if 3 <= c_len <= 6:
                    for node in c:
                        c_info = cycle_info_map[node]
                        c_info["has_loop"] = 1
                        c_info["loop_count"] += 1
                        if c_info["shortest_dist"] == 0 or c_len < c_info["shortest_dist"]:
                            c_info["shortest_dist"] = c_len
                count += 1
        except Exception:
            pass

        # Compile Entity Graph Feature Table
        graph_features = []
        for gstin in df_entities["gstin"]:
            in_deg = in_degrees.get(gstin, 0)
            out_deg = out_degrees.get(gstin, 0)
            tot_deg = in_deg + out_deg
            deg_ratio = float(out_deg) / float(in_deg + 1)
            pr = pagerank_map.get(gstin, 0.0)
            comm_id = community_map.get(gstin, "COMM_000")
            comm_sz = community_size_map.get(gstin, 1)

            c_info = cycle_info_map.get(gstin, {"has_loop": 0, "shortest_dist": 0, "loop_count": 0})

            graph_features.append({
                "gstin": gstin,
                "in_degree": in_deg,
                "out_degree": out_deg,
                "total_degree": tot_deg,
                "degree_ratio": deg_ratio,
                "pagerank": pr,
                "community_id": comm_id,
                "community_size": comm_sz,
                "has_loop": c_info["has_loop"],
                "shortest_loop_dist": c_info["shortest_dist"],
                "loop_count": c_info["loop_count"]
            })

        return pd.DataFrame(graph_features)
