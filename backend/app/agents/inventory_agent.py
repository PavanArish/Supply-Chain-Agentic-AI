import pandas as pd
from typing import Dict, Any


def _find_col(roles: Dict[str, str], role: str):
    for col, r in roles.items():
        if r == role:
            return col
    return None


def run(df: pd.DataFrame, roles: Dict[str, str], query: str) -> Dict[str, Any]:
    insights, charts, recommendations, risk_alerts = [], [], [], []

    inv_col = _find_col(roles, "inventory")
    qty_col = _find_col(roles, "quantity")
    product_col = _find_col(roles, "product")

    level_col = inv_col or qty_col
    if not level_col:
        insights.append("No inventory/stock or quantity column found — cannot assess stock levels.")
        return {"insights": insights, "charts": charts, "recommendations": recommendations, "risk_alerts": risk_alerts}

    series = df[level_col].dropna()
    if series.empty:
        insights.append(f"'{level_col}' column has no usable values.")
        return {"insights": insights, "charts": charts, "recommendations": recommendations, "risk_alerts": risk_alerts}

    low_threshold = series.quantile(0.1)
    low_stock = df[df[level_col] <= low_threshold]

    insights.append(
        f"Average '{level_col}' is {series.mean():.1f}; {len(low_stock)} record(s) are in the "
        f"bottom 10% (≤ {low_threshold:.1f}), signaling potential shortages."
    )

    if product_col and not low_stock.empty:
        top_low = low_stock[product_col].value_counts().head(5)
        charts.append({
            "type": "bar", "title": f"Low-stock items by {product_col}",
            "x": product_col, "data": top_low.to_dict(),
        })
        recommendations.append(
            f"Prioritize restocking: {', '.join(map(str, top_low.index[:3]))} show the most low-stock occurrences."
        )
    else:
        charts.append({
            "type": "histogram", "title": f"Distribution of {level_col}",
            "x": level_col, "data": series.tolist()[:500],
        })

    if len(low_stock) / len(df) > 0.15 if len(df) else False:
        risk_alerts.append(
            f"{len(low_stock)} of {len(df)} records ({len(low_stock)/len(df)*100:.0f}%) are near-critical "
            f"stock levels."
        )

    return {"insights": insights, "charts": charts, "recommendations": recommendations, "risk_alerts": risk_alerts}
