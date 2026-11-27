"""
Heuristic, dataset-agnostic column role detection.
Maps arbitrary column names (e.g. "Ship Date", "Supplier Name", "Delay (days)")
to canonical roles the agents understand, using keyword matching + dtype checks.
No exact naming is required.
"""
import pandas as pd
from typing import Dict

ROLE_KEYWORDS = {
    "date": ["date", "time", "timestamp", "eta", "etd", "created", "shipped", "delivery"],
    "supplier": ["supplier", "vendor", "manufacturer", "seller", "provider"],
    "product": ["product", "item", "sku", "material", "goods"],
    "quantity": ["qty", "quantity", "units", "amount", "count", "volume"],
    "delay": ["delay", "late", "lag"],
    "status": ["status", "state", "condition"],
    "location": ["location", "origin", "destination", "warehouse", "region", "city", "country", "route"],
    "cost": ["cost", "price", "value", "revenue", "expense"],
    "inventory": ["inventory", "stock", "reorder", "on_hand", "on hand"],
    "risk": ["risk", "score"],
    "id": ["id", "code", "reference", "order", "shipment"],
}


def detect_column_roles(df: pd.DataFrame) -> Dict[str, str]:
    roles: Dict[str, str] = {}
    for col in df.columns:
        col_lower = str(col).lower().strip()
        matched_role = None

        # Keyword match first
        for role, keywords in ROLE_KEYWORDS.items():
            if any(kw in col_lower for kw in keywords):
                matched_role = role
                break

        # Fall back to dtype-based guesses
        if matched_role is None:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                matched_role = "date"
            elif pd.api.types.is_numeric_dtype(df[col]):
                matched_role = "numeric"
            else:
                matched_role = "categorical"

        roles[col] = matched_role
    return roles


def coerce_dates(df: pd.DataFrame, roles: Dict[str, str]) -> pd.DataFrame:
    for col, role in roles.items():
        if role == "date":
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
                pass
    return df
