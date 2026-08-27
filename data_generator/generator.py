"""
GST Synthetic Dataset Orchestrator.
Generates reproducible synthetic business entities, transaction invoices, and fraud labels.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from data_generator.normal_transactions import NormalTransactionGenerator
from data_generator.fraud_injection import FraudInjectionEngine

class GSTDataGenerator:
    """Master orchestrator for GST synthetic dataset generation."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.normal_gen = NormalTransactionGenerator(seed=seed)
        self.fraud_engine = FraudInjectionEngine(seed=seed)

    def generate(
        self,
        num_entities: int = 1000,
        num_transactions: int = 10000,
        fraud_rate: float = 0.05,
        output_dir: str = None
    ) -> dict[str, pd.DataFrame]:
        """
        Executes full synthetic dataset generation pipeline.
        Returns dictionary containing DataFrames: 'entities', 'transactions', 'fraud_labels'.
        """
        # 1. Generate Business Entities
        entities = self.normal_gen.generate_entities(num_entities)
        entity_map = {e["gstin"]: e for e in entities}

        # 2. Determine Fraud Target Count
        target_fraud_txs = int(num_transactions * fraud_rate)
        start_date = datetime.now() - timedelta(days=180)

        all_transactions = []
        all_flagged_gstins = set()
        current_inv_counter = 1

        # 3. Inject Fraud Archetypes
        # Split target fraud count across archetypes
        sub_target = max(1, target_fraud_txs // 4)

        # A. Circular Trading (cycles of 3-4 entities)
        num_cycles = max(1, sub_target // 3)
        circ_txs, circ_flagged, current_inv_counter = self.fraud_engine.inject_circular_trading(
            entities=entities,
            start_invoice_id=current_inv_counter,
            start_date=start_date,
            cycle_length=3,
            num_cycles=num_cycles,
            normal_gen_ref=self.normal_gen
        )
        all_transactions.extend(circ_txs)
        all_flagged_gstins.update(circ_flagged)

        # B. Star Collusion
        num_stars = max(1, sub_target // 8)
        star_txs, star_flagged, current_inv_counter = self.fraud_engine.inject_star_collusion(
            entities=entities,
            start_invoice_id=current_inv_counter,
            start_date=start_date,
            num_stars=num_stars,
            spokes_per_star=8,
            normal_gen_ref=self.normal_gen
        )
        all_transactions.extend(star_txs)
        all_flagged_gstins.update(star_flagged)

        # C. Split Invoicing
        num_splits = max(1, sub_target // 10)
        split_txs, split_flagged, current_inv_counter = self.fraud_engine.inject_split_invoicing(
            entities=entities,
            start_invoice_id=current_inv_counter,
            start_date=start_date,
            num_split_groups=num_splits,
            splits_per_group=10,
            normal_gen_ref=self.normal_gen
        )
        all_transactions.extend(split_txs)
        all_flagged_gstins.update(split_flagged)

        # D. High Velocity
        num_velocity = max(1, sub_target // 25)
        vel_txs, vel_flagged, current_inv_counter = self.fraud_engine.inject_high_velocity(
            entities=entities,
            start_invoice_id=current_inv_counter,
            start_date=start_date,
            num_velocity_entities=num_velocity,
            burst_count=25,
            normal_gen_ref=self.normal_gen
        )
        all_transactions.extend(vel_txs)
        all_flagged_gstins.update(vel_flagged)

        # Update entity fraud flags
        for e in entities:
            if e["gstin"] in all_flagged_gstins:
                e["is_fraud_flagged"] = 1

        # 4. Generate Normal Background Transactions
        remaining_txs = max(0, num_transactions - len(all_transactions))
        for _ in range(remaining_txs):
            seller, buyer = random.sample(entities, 2)
            tx_date = start_date + timedelta(
                days=random.randint(0, 180),
                seconds=random.randint(0, 86400)
            )
            tx = self.normal_gen.generate_single_transaction(
                invoice_id=f"INV_NORM_{current_inv_counter:07d}",
                seller=seller,
                buyer=buyer,
                invoice_date=tx_date
            )
            all_transactions.append(tx)
            current_inv_counter += 1

        # 5. Convert to DataFrames
        df_entities = pd.DataFrame(entities)
        df_transactions = pd.DataFrame(all_transactions)

        # Sort transactions chronologically
        df_transactions["invoice_date"] = pd.to_datetime(df_transactions["invoice_date"])
        df_transactions = df_transactions.sort_values(by="invoice_date").reset_index(drop=True)
        df_transactions["invoice_date"] = df_transactions["invoice_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

        # Create Ground-Truth Labels DataFrame
        df_fraud_labels = df_transactions[df_transactions["is_fraud"] == 1][[
            "invoice_id", "seller_gstin", "buyer_gstin", "fraud_pattern", "fraud_group_id", "is_fraud"
        ]].copy()

        # Save to disk if output_dir provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            df_entities.to_csv(os.path.join(output_dir, "entities.csv"), index=False)
            df_transactions.to_csv(os.path.join(output_dir, "transactions.csv"), index=False)
            df_fraud_labels.to_csv(os.path.join(output_dir, "fraud_labels.csv"), index=False)

        return {
            "entities": df_entities,
            "transactions": df_transactions,
            "fraud_labels": df_fraud_labels
        }
