"""
Neo4j Graph Ingestion Module.
Ingests entity nodes and transaction relationships from CSV/DataFrames into Neo4j graph database.
Includes dry-run and fallback handling if Neo4j service is offline.
"""

import os
import logging
import pandas as pd
from dotenv import load_dotenv

from graph.schema import (
    CREATE_BUSINESS_CONSTRAINT,
    CREATE_BUSINESS_INDEXES,
    CREATE_TRANSACTION_INDEXES,
    INGEST_BUSINESS_NODES_CYPHER,
    INGEST_TRANSACTION_EDGES_CYPHER
)
from graph.queries import COUNT_NODES_AND_EDGES

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Neo4jGraphIngestor:
    """Manages batch graph ingestion of GST entities and transaction edges into Neo4j."""

    def __init__(self, uri: str = None, user: str = None, password: str = None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        self.is_connected = False

        self._connect()

    def _connect(self):
        """Attempts connection to Neo4j database."""
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connectivity
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.info(f"Connected successfully to Neo4j instance at {self.uri}")
        except Exception as e:
            self.is_connected = False
            logger.warning(f"Unable to connect to Neo4j at {self.uri}. Operating in DRY-RUN / OFFLINE mode. Error: {e}")

    def close(self):
        """Closes Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver connection closed.")

    def setup_schema(self):
        """Creates uniqueness constraints and indexes in Neo4j."""
        if not self.is_connected:
            logger.info("[Dry-Run] Skipped schema creation (Neo4j offline).")
            return

        with self.driver.session() as session:
            logger.info("Setting up Business GSTIN uniqueness constraint...")
            try:
                session.run(CREATE_BUSINESS_CONSTRAINT)
            except Exception as e:
                logger.warning(f"Constraint setup note: {e}")

            logger.info("Setting up Business indexes...")
            for idx_query in CREATE_BUSINESS_INDEXES:
                session.run(idx_query)

            logger.info("Setting up Transaction indexes...")
            for tx_query in CREATE_TRANSACTION_INDEXES:
                session.run(tx_query)

            logger.info("Neo4j Schema setup completed.")

    def ingest_entities(self, df_entities: pd.DataFrame, batch_size: int = 1000) -> int:
        """Ingests Business nodes in batches."""
        records = df_entities.to_dict(orient="records")
        total = len(records)

        if not self.is_connected:
            logger.info(f"[Dry-Run] Validated {total} Business nodes for ingestion.")
            return total

        logger.info(f"Ingesting {total} Business nodes into Neo4j...")
        ingested_count = 0

        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = records[i:i + batch_size]
                session.run(INGEST_BUSINESS_NODES_CYPHER, batch=batch)
                ingested_count += len(batch)

        logger.info(f"Successfully ingested {ingested_count} Business nodes.")
        return ingested_count

    def ingest_transactions(self, df_transactions: pd.DataFrame, batch_size: int = 1000) -> int:
        """Ingests TRANSACTION directed relationships in batches."""
        records = df_transactions.to_dict(orient="records")
        total = len(records)

        if not self.is_connected:
            logger.info(f"[Dry-Run] Validated {total} TRANSACTION relationships for ingestion.")
            return total

        logger.info(f"Ingesting {total} TRANSACTION relationships into Neo4j...")
        ingested_count = 0

        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = records[i:i + batch_size]
                session.run(INGEST_TRANSACTION_EDGES_CYPHER, batch=batch)
                ingested_count += len(batch)

        logger.info(f"Successfully ingested {ingested_count} TRANSACTION relationships.")
        return ingested_count

    def verify_graph_counts(self) -> dict:
        """Queries Neo4j for node and relationship counts."""
        if not self.is_connected:
            return {"node_count": 0, "edge_count": 0, "status": "OFFLINE"}

        with self.driver.session() as session:
            result = session.run(COUNT_NODES_AND_EDGES).single()
            return {
                "node_count": result["node_count"],
                "edge_count": result["edge_count"],
                "status": "ONLINE"
            }
