# AI-Powered Graph-Based GST Fraud Detection & Risk Intelligence Platform

A B.Tech AIML final-year project presenting an end-to-end platform for detecting circular trading, star-shaped collusion, split invoicing, and high-velocity fraud in GST (Goods and Services Tax) networks.

## Architecture

```
Synthetic GST Transactions → Neo4j Time-Aware Graph → Feature Engineering → GraphSAGE Embeddings → Hybrid Fusion Engine → Contrastive Refinement → Isolation Forest → Risk Score Propagation → Tax Auditor & MSME Portals
```

## Proposed Novelties
1. **Hybrid Fusion Engine**: Combines transactional metrics, manual graph topology features, and self-supervised GNN embeddings into a unified feature representation.
2. **Contrastive Representation Refinement**: Self-supervised representation enhancement without requiring real fraud ground-truth labels.
3. **Risk Score Propagation**: Time and hop-decayed risk propagation through 1–2 hop business supplier-buyer chains.

## Project Directory Structure

```
gst-fraud-platform/
├── backend/            # FastAPI backend routes & services
├── data/               # Raw, processed, and generated datasets
├── data_generator/     # Configurable GST transaction synthetic generator & fraud injector
├── graph/              # Neo4j Cypher schemas, queries, and Python ingestion engine
├── ml/                 # Feature extraction, GraphSAGE, Contrastive learning, Isolation Forest
├── explainability/     # Natural language alert generator & feature analyzer
├── frontend/           # React + Vite dual-portal web application
├── scripts/            # CLI automation scripts
└── tests/              # Pytest automated test suite
```

## Quick Start (Week 1 Data Generation & Graph Ingestion)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Synthetic Data**:
   ```bash
   python scripts/generate_data.py --entities 1000 --transactions 10000 --fraud-rate 0.05 --seed 42
   ```

3. **Ingest Data into Neo4j** (Optional if local Neo4j instance is running):
   ```bash
   python scripts/ingest_graph.py
   ```

4. **Run Unit Tests**:
   ```bash
   pytest
   ```

5. **Run Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
