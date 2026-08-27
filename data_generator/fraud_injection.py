"""
GST Fraud Injection Engine.
Injects controlled synthetic fraud patterns with explicit ground-truth labels for evaluation:
- Circular Trading (Carousel Fraud)
- Star-Shaped Collusion (Hub & Shell Network)
- Split Invoicing (Threshold Evasion)
- High Transaction Velocity (Burst Dumping)
"""

import random
from datetime import datetime, timedelta
import numpy as np
from data_generator.config import FRAUD_TYPES

class FraudInjectionEngine:
    """Injects realistic GST fraud archetypes into transaction graph datasets."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def inject_circular_trading(
        self,
        entities: list[dict],
        start_invoice_id: int,
        start_date: datetime,
        cycle_length: int = 3,
        num_cycles: int = 5,
        normal_gen_ref = None
    ) -> tuple[list[dict], set[str], int]:
        """
        Injects Circular Trading patterns (A -> B -> C -> A).
        Creates closed loop transaction chains passing inflated amounts.
        """
        injected_txs = []
        flagged_gstins = set()
        current_inv_id = start_invoice_id

        for c_idx in range(num_cycles):
            group_id = f"GROUP_CIRC_{c_idx + 1:03d}"
            # Select cycle_length distinct entities
            cycle_nodes = random.sample(entities, cycle_length)
            for node in cycle_nodes:
                flagged_gstins.add(node["gstin"])

            base_amount = float(random.uniform(500000, 5000000))
            cycle_start_time = start_date + timedelta(days=random.randint(0, 180))

            # Complete the loop
            for i in range(cycle_length):
                seller = cycle_nodes[i]
                buyer = cycle_nodes[(i + 1) % cycle_length]

                # Slight variation in amount (0.5% - 2% fee/margin added)
                amount = base_amount * (1.0 + random.uniform(0.005, 0.02) * i)
                tx_date = cycle_start_time + timedelta(hours=i * 6 + random.randint(1, 3))

                tx = normal_gen_ref.generate_single_transaction(
                    invoice_id=f"INV_FRD_{current_inv_id:07d}",
                    seller=seller,
                    buyer=buyer,
                    invoice_date=tx_date,
                    amount_override=amount
                )
                tx["fraud_pattern"] = FRAUD_TYPES["CIRCULAR_TRADING"]
                tx["fraud_group_id"] = group_id
                tx["is_fraud"] = 1
                injected_txs.append(tx)
                current_inv_id += 1

        return injected_txs, flagged_gstins, current_inv_id

    def inject_star_collusion(
        self,
        entities: list[dict],
        start_invoice_id: int,
        start_date: datetime,
        num_stars: int = 3,
        spokes_per_star: int = 8,
        normal_gen_ref = None
    ) -> tuple[list[dict], set[str], int]:
        """
        Injects Star-Shaped Collusion networks.
        A central shell entity receives/sends multiple fraudulent invoices from/to surrounding nodes.
        """
        injected_txs = []
        flagged_gstins = set()
        current_inv_id = start_invoice_id

        for s_idx in range(num_stars):
            group_id = f"GROUP_STAR_{s_idx + 1:03d}"
            center = random.choice(entities)
            flagged_gstins.add(center["gstin"])

            # Filter candidates excluding center
            candidates = [e for e in entities if e["gstin"] != center["gstin"]]
            spokes = random.sample(candidates, min(spokes_per_star, len(candidates)))

            star_time = start_date + timedelta(days=random.randint(0, 180))

            for spoke in spokes:
                flagged_gstins.add(spoke["gstin"])
                amount = float(random.uniform(200000, 2500000))
                tx_date = star_time + timedelta(minutes=random.randint(10, 360))

                # Half incoming to center, half outgoing
                is_incoming = random.choice([True, False])
                seller = spoke if is_incoming else center
                buyer = center if is_incoming else spoke

                tx = normal_gen_ref.generate_single_transaction(
                    invoice_id=f"INV_FRD_{current_inv_id:07d}",
                    seller=seller,
                    buyer=buyer,
                    invoice_date=tx_date,
                    amount_override=amount
                )
                tx["fraud_pattern"] = FRAUD_TYPES["STAR_COLLUSION"]
                tx["fraud_group_id"] = group_id
                tx["is_fraud"] = 1
                injected_txs.append(tx)
                current_inv_id += 1

        return injected_txs, flagged_gstins, current_inv_id

    def inject_split_invoicing(
        self,
        entities: list[dict],
        start_invoice_id: int,
        start_date: datetime,
        num_split_groups: int = 5,
        splits_per_group: int = 10,
        normal_gen_ref = None
    ) -> tuple[list[dict], set[str], int]:
        """
        Injects Split Invoicing (Threshold Evasion).
        Large transactions split into multiple transactions just below statutory audit limits (e.g. ₹49,000-₹49,900).
        """
        injected_txs = []
        flagged_gstins = set()
        current_inv_id = start_invoice_id

        for sp_idx in range(num_split_groups):
            group_id = f"GROUP_SPLIT_{sp_idx + 1:03d}"
            seller, buyer = random.sample(entities, 2)
            flagged_gstins.add(seller["gstin"])
            flagged_gstins.add(buyer["gstin"])

            split_time = start_date + timedelta(days=random.randint(0, 180))

            for i in range(splits_per_group):
                # Generates amounts between ₹47,500 and ₹49,800 to evade ₹50,000 e-way bill threshold
                sub_threshold_amount = float(random.uniform(47500, 49800))
                tx_date = split_time + timedelta(minutes=i * 15 + random.randint(1, 5))

                tx = normal_gen_ref.generate_single_transaction(
                    invoice_id=f"INV_FRD_{current_inv_id:07d}",
                    seller=seller,
                    buyer=buyer,
                    invoice_date=tx_date,
                    amount_override=sub_threshold_amount
                )
                tx["fraud_pattern"] = FRAUD_TYPES["SPLIT_INVOICING"]
                tx["fraud_group_id"] = group_id
                tx["is_fraud"] = 1
                injected_txs.append(tx)
                current_inv_id += 1

        return injected_txs, flagged_gstins, current_inv_id

    def inject_high_velocity(
        self,
        entities: list[dict],
        start_invoice_id: int,
        start_date: datetime,
        num_velocity_entities: int = 3,
        burst_count: int = 35,
        normal_gen_ref = None
    ) -> tuple[list[dict], set[str], int]:
        """
        Injects High Transaction Velocity (Burst Fraud).
        A single entity generates an unnaturally dense burst of transactions in a short window.
        """
        injected_txs = []
        flagged_gstins = set()
        current_inv_id = start_invoice_id

        for v_idx in range(num_velocity_entities):
            group_id = f"GROUP_VELOCITY_{v_idx + 1:03d}"
            seller = random.choice(entities)
            flagged_gstins.add(seller["gstin"])

            other_entities = [e for e in entities if e["gstin"] != seller["gstin"]]
            burst_start = start_date + timedelta(days=random.randint(10, 150))

            for b in range(burst_count):
                buyer = random.choice(other_entities)
                amount = float(random.uniform(100000, 800000))
                # Burst happens over 24-48 hours
                tx_date = burst_start + timedelta(minutes=b * 40 + random.randint(1, 10))

                tx = normal_gen_ref.generate_single_transaction(
                    invoice_id=f"INV_FRD_{current_inv_id:07d}",
                    seller=seller,
                    buyer=buyer,
                    invoice_date=tx_date,
                    amount_override=amount
                )
                tx["fraud_pattern"] = FRAUD_TYPES["HIGH_VELOCITY"]
                tx["fraud_group_id"] = group_id
                tx["is_fraud"] = 1
                injected_txs.append(tx)
                current_inv_id += 1

        return injected_txs, flagged_gstins, current_inv_id
