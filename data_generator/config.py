"""
Configuration constants for GST Data Generation.
"""

# Indian States with valid 2-digit GST state codes
STATE_CODES = {
    "01": "Jammu & Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "27": "Maharashtra",
    "29": "Karnataka",
    "30": "Goa",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "36": "Telangana",
    "37": "Andhra Pradesh"
}

# Standard GST Tax Rates (in percentage)
TAX_SLABS = [5.0, 12.0, 18.0, 28.0]
TAX_SLAB_WEIGHTS = [0.15, 0.25, 0.45, 0.15]

# Business Size Categories
BUSINESS_SIZES = ["Micro", "Small", "Medium", "Large Enterprise"]
BUSINESS_SIZE_WEIGHTS = [0.50, 0.30, 0.15, 0.05]

# Product Categories
PRODUCT_CATEGORIES = [
    "Electronics & Appliances",
    "Textiles & Apparel",
    "Metals & Scrap",
    "Chemicals & Fertilizers",
    "FMCG & Grocery",
    "Building & Construction Materials",
    "Auto Components",
    "IT Services & Software",
    "Pharmaceuticals"
]

# Payment Modes
PAYMENT_MODES = ["NEFT/RTGS", "UPI", "Cheque", "NetBanking", "Cash"]
PAYMENT_MODE_WEIGHTS = [0.55, 0.20, 0.15, 0.08, 0.02]

# Transaction Statuses
TRANSACTION_STATUSES = ["COMPLETED", "SETTLED", "RECONCILED", "PENDING"]

# Fraud Archetypes
FRAUD_TYPES = {
    "CIRCULAR_TRADING": "circular_trading",
    "STAR_COLLUSION": "star_collusion",
    "SPLIT_INVOICING": "split_invoicing",
    "HIGH_VELOCITY": "high_velocity"
}
