"""
Neo4j Graph Schema Definitions, Constraints, and Index Creation Queries.
"""

# Neo4j Cypher DDL Queries
CREATE_BUSINESS_CONSTRAINT = """
CREATE CONSTRAINT business_gstin_unique IF NOT EXISTS
FOR (b:Business) REQUIRE b.gstin IS UNIQUE;
"""

CREATE_BUSINESS_INDEXES = [
    """
    CREATE INDEX business_state_idx IF NOT EXISTS
    FOR (b:Business) ON (b.state);
    """,
    """
    CREATE INDEX business_category_idx IF NOT EXISTS
    FOR (b:Business) ON (b.category);
    """
]

CREATE_TRANSACTION_INDEXES = [
    """
    CREATE INDEX transaction_invoice_id_idx IF NOT EXISTS
    FOR ()-[r:TRANSACTION]-() ON (r.invoice_id);
    """,
    """
    CREATE INDEX transaction_date_idx IF NOT EXISTS
    FOR ()-[r:TRANSACTION]-() ON (r.invoice_date);
    """
]

# Cypher Batch Ingestion Templates
INGEST_BUSINESS_NODES_CYPHER = """
UNWIND $batch AS row
MERGE (b:Business {gstin: row.gstin})
ON CREATE SET
    b.state_code = row.state_code,
    b.state = row.state,
    b.business_size = row.business_size,
    b.category = row.category,
    b.registration_age_months = toInteger(row.registration_age_months),
    b.base_volume = toInteger(row.base_volume),
    b.avg_amount = toFloat(row.avg_amount),
    b.is_fraud_flagged = toInteger(row.is_fraud_flagged)
ON MATCH SET
    b.business_size = row.business_size,
    b.category = row.category,
    b.is_fraud_flagged = toInteger(row.is_fraud_flagged);
"""

INGEST_TRANSACTION_EDGES_CYPHER = """
UNWIND $batch AS row
MATCH (s:Business {gstin: row.seller_gstin})
MATCH (b:Business {gstin: row.buyer_gstin})
CREATE (s)-[r:TRANSACTION {
    invoice_id: row.invoice_id,
    invoice_number: row.invoice_number,
    invoice_date: row.invoice_date,
    taxable_amount: toFloat(row.taxable_amount),
    tax_rate: toFloat(row.tax_rate),
    cgst: toFloat(row.cgst),
    sgst: toFloat(row.sgst),
    igst: toFloat(row.igst),
    total_invoice_amount: toFloat(row.total_invoice_amount),
    seller_state: row.seller_state,
    buyer_state: row.buyer_state,
    product_category: row.product_category,
    payment_mode: row.payment_mode,
    transaction_status: row.transaction_status,
    fraud_pattern: row.fraud_pattern,
    is_fraud: toInteger(row.is_fraud)
}]->(b);
"""
