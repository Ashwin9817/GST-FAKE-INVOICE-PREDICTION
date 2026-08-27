"""
Explainable Fraud Alert Generator Module.
Generates human-readable natural language alerts and structured explanation breakdowns tied to computed quantitative features.
"""

class ExplainableAlertGenerator:
    """Generates explainable natural language alerts and structured feature reason breakdowns."""

    def generate_explanation(
        self,
        gstin: str,
        risk_profile: dict,
        feature_profile: dict = None
    ) -> dict:
        """
        Generates structured explanation breakdown and natural language alert paragraph.
        """
        risk_score = risk_profile.get("final_risk_score", risk_profile.get("risk_score", 15.0))
        risk_cat = risk_profile.get("risk_category", "LOW")
        direct_risk = risk_profile.get("direct_risk_score", risk_score)
        propagated_risk = risk_profile.get("propagated_network_risk", 0.0)

        feats = feature_profile or {}

        reasons = []

        # 1. Circular Loop Reason
        has_loop = feats.get("has_loop", 0)
        shortest_dist = feats.get("shortest_loop_dist", 0)
        if has_loop or shortest_dist > 0:
            dist_str = f"{shortest_dist}-hop" if shortest_dist > 0 else "multi-hop"
            reasons.append({
                "code": "CIRCULAR_PATH",
                "severity": "HIGH",
                "description": f"Participates in a {dist_str} closed circular transaction chain passing bogus invoices."
            })

        # 2. Transaction Velocity Reason
        tx_day = feats.get("tx_per_day", 0.0)
        burst_24h = feats.get("burst_24h_max", 0)
        if burst_24h > 15 or tx_day > 10.0:
            reasons.append({
                "code": "HIGH_VELOCITY",
                "severity": "HIGH",
                "description": f"Exhibits abnormal transaction velocity ({burst_24h} invoices issued in a 24-hour window)."
            })

        # 3. Rapid Repeat Counterparties
        rapid_repeat = feats.get("rapid_repeat_count", 0)
        if rapid_repeat > 3:
            reasons.append({
                "code": "RAPID_REPEAT_TRADES",
                "severity": "MEDIUM",
                "description": f"Generates {rapid_repeat} rapid repeated transactions with identical counterparties within 24 hours."
            })

        # 4. Propagated Risk Reason
        if propagated_risk >= 30.0:
            reasons.append({
                "code": "PROPAGATED_NETWORK_RISK",
                "severity": "HIGH" if propagated_risk >= 60.0 else "MEDIUM",
                "description": f"Exposed to network risk (propagated risk indicator: {propagated_risk:.1f}/100) via 1-2 hop connections to flagged entities."
            })

        # 5. PageRank / Centrality Reason
        pr = feats.get("pagerank", 0.0)
        if pr > 0.01:
            reasons.append({
                "code": "HIGH_STRUCTURAL_CENTRALITY",
                "severity": "MEDIUM",
                "description": f"Displays high PageRank structural centrality ({pr:.4f}) within invoice credit flow graph."
            })

        # Fallback if no specific threshold breached
        if not reasons:
            if risk_cat == "HIGH":
                reasons.append({
                    "code": "ANOMALOUS_FEATURE_VECTOR",
                    "severity": "HIGH",
                    "description": "Multi-dimensional anomaly detected across hybrid transactional and GNN embedding representations."
                })
            else:
                reasons.append({
                    "code": "NORMAL_OPERATIONAL_PATTERN",
                    "severity": "LOW",
                    "description": "Transaction volume, tax breakdown, and network topology conform to normal baseline behavior."
                })

        # Construct Natural Language Alert Narrative
        reason_texts = [r["description"] for r in reasons if r["severity"] in ["HIGH", "MEDIUM"]]
        if not reason_texts:
            reason_texts = [r["description"] for r in reasons]

        nl_summary = f"Entity {gstin} is classified as {risk_cat} RISK (Score: {risk_score:.1f}/100) because it " + " ".join(reason_texts)

        return {
            "gstin": gstin,
            "risk_score": risk_score,
            "risk_category": risk_cat,
            "direct_risk_score": direct_risk,
            "propagated_network_risk": propagated_risk,
            "reasons": reasons,
            "natural_language_summary": nl_summary
        }
