"""
FastAPI Backend Application Configuration Settings.
"""

import os

class Settings:
    APP_NAME: str = "GST Fraud Detection & Risk Intelligence API"
    VERSION: str = "1.0.0"
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"

    # Dataset Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    ENTITIES_FILE: str = os.path.join(DATA_DIR, "generated", "entities.csv")
    TRANSACTIONS_FILE: str = os.path.join(DATA_DIR, "generated", "transactions.csv")
    RISK_SCORES_FILE: str = os.path.join(DATA_DIR, "processed", "risk_scores.csv")
    ENTITY_FEATURES_FILE: str = os.path.join(DATA_DIR, "processed", "entity_features.csv")

settings = Settings()
