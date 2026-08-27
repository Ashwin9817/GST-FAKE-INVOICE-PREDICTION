"""
Enhanced FastAPI Main Entrypoint with Explainability, Risk Propagation, and Alerts Endpoint.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.config import settings
from backend.app.services.risk_service import RiskService
from backend.app.services.graph_service import GraphService
from explainability.alert_generator import ExplainableAlertGenerator

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Backend REST API for AI-Powered Graph-Based GST Fraud Detection & Risk Intelligence Platform."
)

# CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

risk_service = RiskService()
graph_service = GraphService()
alert_gen = ExplainableAlertGenerator()


class RiskCheckRequest(BaseModel):
    supplier_gstin: str


# ───────── Health ─────────
@app.get("/api/health", tags=["System"])
def health_check():
    """Returns API health status."""
    return {"status": "ONLINE", "app_name": settings.APP_NAME, "version": settings.VERSION}


# ───────── Platform Stats ─────────
@app.get("/api/stats", tags=["Analytics"])
def get_stats():
    """Returns overall platform metrics (total entities, transactions, risk distribution)."""
    return risk_service.get_system_stats()


# ───────── Entity Profile ─────────
@app.get("/api/entities/{gstin}", tags=["Entity"])
def get_entity_profile(gstin: str):
    """Returns entity metadata, topological metrics, direct & propagated risk scores."""
    res = risk_service.get_entity_profile(gstin)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


# ───────── Entity Transactions ─────────
@app.get("/api/entities/{gstin}/transactions", tags=["Entity"])
def get_entity_transactions(gstin: str, limit: int = Query(50, ge=1, le=200)):
    """Returns transaction invoice log for a given GSTIN."""
    return risk_service.get_entity_transactions(gstin, limit=limit)


# ───────── 1-2 Hop Network Subgraph ─────────
@app.get("/api/entities/{gstin}/network", tags=["Graph"])
def get_entity_network(gstin: str, hops: int = Query(1, ge=1, le=2)):
    """Returns 1-hop or 2-hop transaction network subgraph in nodes/edges format."""
    return graph_service.get_network_subgraph(gstin, hops=hops)


# ───────── Explainable Alert ─────────
@app.get("/api/entities/{gstin}/alert", tags=["Explainability"])
def get_entity_alert(gstin: str):
    """Returns structured explainability alert with reasons and natural language summary."""
    profile = risk_service.get_entity_profile(gstin)
    if "error" in profile:
        raise HTTPException(status_code=404, detail=profile["error"])

    risk_info = profile.get("risk", {})
    feat_info = profile.get("features", {})

    explanation = alert_gen.generate_explanation(
        gstin=gstin.upper().strip(),
        risk_profile=risk_info,
        feature_profile=feat_info
    )
    return explanation


# ───────── MSME Supplier Verification ─────────
@app.post("/api/risk-check", tags=["MSME"])
def verify_supplier_risk(payload: RiskCheckRequest):
    """Verifies supplier risk status for an MSME buyer before transacting."""
    return risk_service.verify_msme_supplier(payload.supplier_gstin)


# ───────── Ranked High-Risk Entities List ─────────
@app.get("/api/high-risk", tags=["Analytics"])
def get_high_risk_entities(limit: int = Query(20, ge=1, le=100)):
    """Returns top N high-risk entities ranked by final risk score."""
    return risk_service.get_high_risk_entities(limit=limit)
