"""
Cypher Queries for Verification, Structural Metrics, and Network Traversal.
"""

COUNT_NODES_AND_EDGES = """
MATCH (b:Business)
OPTIONAL MATCH ()-[r:TRANSACTION]->()
RETURN count(DISTINCT b) AS node_count, count(r) AS edge_count;
"""

GET_ENTITY_1HOP_NETWORK = """
MATCH (center:Business {gstin: $gstin})
OPTIONAL MATCH (center)-[out:TRANSACTION]->(buyer:Business)
OPTIONAL MATCH (supplier:Business)-[inc:TRANSACTION]->(center)
RETURN center,
       collect(DISTINCT buyer) AS buyers,
       collect(DISTINCT out) AS outgoing_txs,
       collect(DISTINCT supplier) AS suppliers,
       collect(DISTINCT inc) AS incoming_txs;
"""

DETECT_CIRCULAR_PATHS_CYPHER = """
MATCH path = (a:Business {gstin: $gstin})-[r:TRANSACTION*3..6]->(a)
RETURN path, [node IN nodes(path) | node.gstin] AS gstin_cycle, length(path) AS cycle_length
LIMIT 10;
"""

GET_TOP_DEGREE_NODES = """
MATCH (b:Business)
OPTIONAL MATCH (b)-[out:TRANSACTION]->()
OPTIONAL MATCH ()-[inc:TRANSACTION]->(b)
WITH b, count(DISTINCT out) AS out_degree, count(DISTINCT inc) AS in_degree
RETURN b.gstin AS gstin, b.state AS state, b.category AS category,
       in_degree, out_degree, (in_degree + out_degree) AS total_degree
ORDER BY total_degree DESC
LIMIT $limit;
"""
