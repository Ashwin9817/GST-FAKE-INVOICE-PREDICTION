"""
Normal GST Transactions & Business Profile Generator.
Generates baseline business profiles and standard non-fraudulent invoice records.
"""

import random
from datetime import datetime, timedelta
import numpy as np
from data_generator.config import (
    TAX_SLABS, TAX_SLAB_WEIGHTS,
    BUSINESS_SIZES, BUSINESS_SIZE_WEIGHTS,
    PRODUCT_CATEGORIES, PAYMENT_MODES, PAYMENT_MODE_WEIGHTS,
    TRANSACTION_STATUSES
)
from data_generator.gstin_generator import GSTINGenerator

class NormalTransactionGenerator:
    """Generates realistic normal business entities and GST transaction records."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.gstin_gen = GSTINGenerator(seed=seed)

    def generate_entities(self, count: int) -> list[dict]:
        """Generates business entity profiles with synthetic operational metadata."""
        raw_entities = self.gstin_gen.generate_batch(count)
        entities = []

        for entity in raw_entities:
            size = np.random.choice(BUSINESS_SIZES, p=BUSINESS_SIZE_WEIGHTS)
            category = random.choice(PRODUCT_CATEGORIES)
            reg_age_months = random.randint(3, 120)

            # Assign typical baseline monthly transaction capacity based on business size
            if size == "Micro":
                base_volume = random.randint(5, 30)
                avg_amount = random.uniform(5000, 50000)
            elif size == "Small":
                base_volume = random.randint(30, 100)
                avg_amount = random.uniform(50000, 200000)
            elif size == "Medium":
                base_volume = random.randint(100, 300)
                avg_amount = random.uniform(200000, 1000000)
            else:  # Large Enterprise
                base_volume = random.randint(300, 1000)
                avg_amount = random.uniform(1000000, 5000000)

            entities.append({
                "gstin": entity["gstin"],
                "state_code": entity["state_code"],
                "state": entity["state"],
                "business_size": size,
                "category": category,
                "registration_age_months": reg_age_months,
                "base_volume": base_volume,
                "avg_amount": avg_amount,
                "is_fraud_flagged": 0
            })

        return entities

    def calculate_tax_breakdown(self, taxable_amount: float, tax_rate: float, seller_state: str, buyer_state: str) -> dict:
        """Calculates precise GST tax components based on trade geography."""
        taxable_amount = round(float(taxable_amount), 2)
        tax_amount = round(taxable_amount * (tax_rate / 100.0), 2)

        if seller_state == buyer_state:
            # Intra-state transaction: CGST + SGST
            cgst = round(tax_amount / 2.0, 2)
            sgst = round(tax_amount - cgst, 2)
            igst = 0.0
        else:
            # Inter-state transaction: IGST only
            cgst = 0.0
            sgst = 0.0
            igst = tax_amount

        total_amount = round(taxable_amount + cgst + sgst + igst, 2)

        return {
            "taxable_amount": taxable_amount,
            "tax_rate": tax_rate,
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "total_tax": tax_amount,
            "total_invoice_amount": total_amount
        }

    def generate_single_transaction(
        self,
        invoice_id: str,
        seller: dict,
        buyer: dict,
        invoice_date: datetime,
        amount_override: float = None,
        product_category: str = None
    ) -> dict:
        """Generates a single structured GST transaction invoice."""
        if amount_override is not None:
            taxable_amount = amount_override
        else:
            # Use lognormal distribution centered on seller's average amount
            mean_amt = seller.get("avg_amount", 50000)
            taxable_amount = float(np.random.lognormal(mean=np.log(mean_amt), sigma=0.5))
            taxable_amount = max(1000.0, min(10000000.0, taxable_amount))

        tax_rate = float(np.random.choice(TAX_SLABS, p=TAX_SLAB_WEIGHTS))
        tax_info = self.calculate_tax_breakdown(taxable_amount, tax_rate, seller["state"], buyer["state"])

        category = product_category if product_category else seller["category"]
        payment_mode = str(np.random.choice(PAYMENT_MODES, p=PAYMENT_MODE_WEIGHTS))
        status = str(random.choice(TRANSACTION_STATUSES))
        inv_num = f"INV/{invoice_date.strftime('%Y%m')}/{random.randint(10000, 99999)}"

        return {
            "invoice_id": invoice_id,
            "seller_gstin": seller["gstin"],
            "buyer_gstin": buyer["gstin"],
            "invoice_date": invoice_date.strftime("%Y-%m-%d %H:%M:%S"),
            "invoice_number": inv_num,
            "taxable_amount": tax_info["taxable_amount"],
            "tax_rate": tax_info["tax_rate"],
            "cgst": tax_info["cgst"],
            "sgst": tax_info["sgst"],
            "igst": tax_info["igst"],
            "total_invoice_amount": tax_info["total_invoice_amount"],
            "seller_state": seller["state"],
            "buyer_state": buyer["state"],
            "product_category": category,
            "payment_mode": payment_mode,
            "transaction_status": status,
            "fraud_pattern": "NONE",
            "fraud_group_id": None,
            "is_fraud": 0
        }
