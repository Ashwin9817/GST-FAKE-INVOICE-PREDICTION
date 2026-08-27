"""
Entity-Level Temporal Feature Engineering Module.
Calculates sales, purchases, transaction velocity, counterparty diversity, rapid repeat transactions, and temporal burst metrics.
"""

import pandas as pd
import numpy as np

class TemporalFeatureExtractor:
    """Extracts entity-level temporal and financial transaction behavioral features."""

    def extract_features(self, df_transactions: pd.DataFrame, df_entities: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates entity-level financial and temporal behavioral features.
        Returns a DataFrame indexed by entity GSTIN.
        """
        df_tx = df_transactions.copy()
        df_tx["invoice_date"] = pd.to_datetime(df_tx["invoice_date"])

        all_gstins = df_entities["gstin"].tolist()
        features_list = []

        # Pre-group sales and purchases
        sales_grouped = df_tx.groupby("seller_gstin")
        purchases_grouped = df_tx.groupby("buyer_gstin")

        for gstin in all_gstins:
            # Sales (Outgoing) Metrics
            if gstin in sales_grouped.groups:
                s_df = sales_grouped.get_group(gstin)
                total_sales = float(s_df["total_invoice_amount"].sum())
                sales_count = len(s_df)
                avg_sale = float(s_df["total_invoice_amount"].mean())
                max_sale = float(s_df["total_invoice_amount"].max())
                unique_buyers = s_df["buyer_gstin"].nunique()
                sales_dates = s_df["invoice_date"].sort_values()
            else:
                total_sales = 0.0
                sales_count = 0
                avg_sale = 0.0
                max_sale = 0.0
                unique_buyers = 0
                sales_dates = pd.Series(dtype="datetime64[ns]")

            # Purchases (Incoming) Metrics
            if gstin in purchases_grouped.groups:
                p_df = purchases_grouped.get_group(gstin)
                total_purchases = float(p_df["total_invoice_amount"].sum())
                purchases_count = len(p_df)
                avg_purchase = float(p_df["total_invoice_amount"].mean())
                max_purchase = float(p_df["total_invoice_amount"].max())
                unique_suppliers = p_df["seller_gstin"].nunique()
                purchases_dates = p_df["invoice_date"].sort_values()
            else:
                total_purchases = 0.0
                purchases_count = 0
                avg_purchase = 0.0
                max_purchase = 0.0
                unique_suppliers = 0
                purchases_dates = pd.Series(dtype="datetime64[ns]")

            total_tx_count = sales_count + purchases_count
            total_turnover = total_sales + total_purchases
            net_tax_balance = total_sales - total_purchases
            buyer_supplier_ratio = float(unique_buyers) / float(unique_suppliers + 1)

            # Combine all transaction dates for velocity calculation
            all_dates = pd.concat([sales_dates, purchases_dates]).sort_values()
            if len(all_dates) > 1:
                date_span_days = max(1.0, (all_dates.iloc[-1] - all_dates.iloc[0]).total_seconds() / 86400.0)
            else:
                date_span_days = 1.0

            tx_per_day = total_tx_count / date_span_days
            tx_per_week = tx_per_day * 7.0

            # Calculate 24-hour burst activity (max transactions within 24 hours)
            if len(all_dates) > 0:
                # Rolling window count over 24h
                date_df = pd.DataFrame({"dt": all_dates, "val": 1}).set_index("dt")
                burst_24h = int(date_df.rolling("24h")["val"].sum().max())
            else:
                burst_24h = 0

            # Calculate rapid repeated counterparty transactions (< 24h between trades)
            rapid_repeat_count = 0
            if gstin in sales_grouped.groups:
                s_df = sales_grouped.get_group(gstin).sort_values("invoice_date")
                for _, cp_df in s_df.groupby("buyer_gstin"):
                    if len(cp_df) > 1:
                        time_diffs = cp_df["invoice_date"].diff().dt.total_seconds().dropna()
                        rapid_repeat_count += (time_diffs < 86400.0).sum()

            features_list.append({
                "gstin": gstin,
                "total_sales": total_sales,
                "total_purchases": total_purchases,
                "total_turnover": total_turnover,
                "net_tax_balance": net_tax_balance,
                "sales_count": sales_count,
                "purchases_count": purchases_count,
                "total_tx_count": total_tx_count,
                "avg_sale": avg_sale,
                "max_sale": max_sale,
                "avg_purchase": avg_purchase,
                "max_purchase": max_purchase,
                "unique_buyers": unique_buyers,
                "unique_suppliers": unique_suppliers,
                "buyer_supplier_ratio": buyer_supplier_ratio,
                "tx_per_day": tx_per_day,
                "tx_per_week": tx_per_week,
                "burst_24h_max": burst_24h,
                "rapid_repeat_count": int(rapid_repeat_count)
            })

        return pd.DataFrame(features_list)
